from __future__ import annotations
import asyncio
from asyncio.log import logger
from typing import Any, Awaitable, Callable, List, Optional

from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy.adapters.schemas.tools_schema import ToolsSchema
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.frames.frames import TTSSpeakFrame, BotSpeakingFrame, LLMFullResponseEndFrame
from piopiy.pipeline.pipeline import Pipeline
from piopiy.pipeline.runner import PipelineRunner
from piopiy.pipeline.task import PipelineParams, PipelineTask
from piopiy.processors.frame_processor import FrameProcessor
from piopiy.audio.interruptions.base_interruption_strategy import BaseInterruptionStrategy
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.transports.base_transport import BaseTransport
from piopiy.transports.services.telecmi import TelecmiParams, TelecmiTransport

try:
    from piopiy.processors.aggregators.openai_llm_context import OpenAILLMContext
except Exception:
    OpenAILLMContext = None  # type: ignore


class VoiceAgent:
    def __init__(
        self,
        *,
        instructions: str,
        tools: Optional[List[FunctionSchema]] = None,  # optional; kept for back-compat
        greeting: Optional[str] = None,
        idle_timeout_secs: int = 60,
    ) -> None:
        self._instructions = instructions
        self._messages = [{"role": "system", "content": instructions}]
        self._tools = tools or []  # legacy path; you can omit at callsite
        self._greeting = greeting
        self._idle_timeout_secs = idle_timeout_secs

        # Tool wiring
        self._tool_handlers: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._tool_schemas: dict[str, FunctionSchema] = {}

        # Components (populated by AgentAction)
        self._transport: Optional[BaseTransport] = None
        self._stt: Optional[FrameProcessor] = None
        self._llm: Optional[FrameProcessor] = None
        self._tts: Optional[FrameProcessor] = None
        self._vad: Optional[FrameProcessor] = None

        # Toggles
        self._enable_metrics = False
        self._enable_usage_metrics = False
        self._allow_interruptions = False
        self._interruption_strategy: Optional[BaseInterruptionStrategy] = None

        # Runtime
        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None
        self.context_aggregator = None
        self._processors: List[FrameProcessor] = []
        self._pipe: Optional[Pipeline] = None

    # ---- Tool APIs ----
    def add_tool(self, schema: FunctionSchema, handler: Callable[..., Awaitable[Any]]) -> None:
        """Register schema (model exposure) + handler (runtime) in one call."""
        self._tool_schemas[schema.name] = schema
        self._tool_handlers[schema.name] = handler

    def register_tool(self, name: str, handler: Callable[..., Awaitable[Any]]) -> None:
        """Back-compat: only provide a handler for a tool that was listed in tools=[...]."""
        self._tool_handlers[name] = handler

    # ---- Configuration ----
    async def AgentAction(
        self,
        *,
        stt: FrameProcessor,
        llm: FrameProcessor,
        tts: FrameProcessor,
        mcp_tools: Optional[Any] = None,
        vad: Optional[FrameProcessor] = None,  # pass SileroVADAnalyzer() to enable, or None to disable
        enable_metrics: bool = True,
        enable_usage_metrics: bool = True,
        allow_interruptions: bool = True,
        interruption_strategy: Optional[BaseInterruptionStrategy] = None,
        telecmi_params: Optional[TelecmiParams] = None,
    ) -> None:
        """Store components and toggles; pipeline is built in start()."""
        self._stt = stt
        self._llm = llm
        self._tts = tts
        self._vad = vad
        self._enable_metrics = enable_metrics
        self._enable_usage_metrics = enable_usage_metrics
        self._allow_interruptions = allow_interruptions
        self._interruption_strategy = interruption_strategy

        self._mcp_client = mcp_tools or None

        # Build transport now (VAD goes into TelecmiParams.vad_analyzer)
        if telecmi_params is None:
            telecmi_params = TelecmiParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                audio_out_sample_rate=8000,
                audio_in_sample_rate=16000,
                vad_analyzer=(self._vad if isinstance(self._vad, SileroVADAnalyzer) else None),
            )
        self._transport = TelecmiTransport(params=telecmi_params)

    # ---- Pipeline build & run ----
    async def _build_task(self) -> None:
        """Assemble Pipeline + Task (must be awaited before run)."""
        if not (self._transport and self._stt and self._llm and self._tts):
            raise RuntimeError("Call AgentAction(...) before start(). Missing components.")

        self._processors = [self._transport.input(), self._stt]

        # Consolidate tool schemas from add_tool() and (optionally) ctor tools=[...]
        tool_schemas: List[FunctionSchema] = list(self._tool_schemas.values())
        if self._tools:
            names = {s.name for s in tool_schemas}
            tool_schemas.extend([s for s in self._tools if s.name not in names])

        # Advertise tools to the model via OpenAI context (if available)
        if OpenAILLMContext and hasattr(self._llm, "create_context_aggregator"):
            tools_schema = ToolsSchema(standard_tools=tool_schemas) if tool_schemas else None
            ctx = OpenAILLMContext(self._messages, tools_schema) if tools_schema else OpenAILLMContext(self._messages)
            if self._mcp_client:
                ctx = OpenAILLMContext(self._messages, tools=self._mcp_client) if self._mcp_client else OpenAILLMContext(self._messages)
            self.context_aggregator = self._llm.create_context_aggregator(ctx)
            self._processors.append(self.context_aggregator.user())

        # Register runtime handlers with the LLM service
        # Prefer NAME-based first (Daily/Pipecat style), then fall back to schema-based.
        by_name = {s.name: s for s in tool_schemas}

        if hasattr(self._llm, "register_function"):
            for name, fn in self._tool_handlers.items():
                try:
                    # Most Pipecat builds: (name: str, handler)
                    self._llm.register_function(name, fn)
                except TypeError:
                    # Some variants: (schema: FunctionSchema, handler)
                    schema = by_name.get(name)
                    if schema:
                        self._llm.register_function(schema, fn)

        elif hasattr(self._llm, "register_tool"):
            for name, fn in self._tool_handlers.items():
                try:
                    # Common: (name: str, handler)
                    self._llm.register_tool(name, fn)
                except TypeError:
                    # Others: (schema: FunctionSchema, handler)
                    schema = by_name.get(name)
                    if schema:
                        self._llm.register_tool(schema, fn)
        else:
            raise RuntimeError("LLMService missing register_function/register_tool")

        

        # Finish processor chain
        self._processors.extend([self._llm, self._tts, self._transport.output()])
        if self.context_aggregator:
            self._processors.append(self.context_aggregator.assistant())

        self._pipe = Pipeline(self._processors)

        params = PipelineParams(
            enable_metrics=self._enable_metrics,
            enable_usage_metrics=self._enable_usage_metrics,
            allow_interruptions=self._allow_interruptions,
            interruption_strategy=(
                self._interruption_strategy or MinWordsInterruptionStrategy(min_words=1)
                if self._allow_interruptions else None
            ),
            idle_timeout_secs=self._idle_timeout_secs,
            idle_timeout_frames=(BotSpeakingFrame, LLMFullResponseEndFrame),
            cancel_on_idle_timeout=True,
        )

        self._task = PipelineTask(self._pipe, params=params)
        self._runner = PipelineRunner(handle_sigint=False)

        # ---- Transport events ----
        @self._transport.event_handler("on_first_participant_joined")
        async def _greet(_, _pid):
            if self._greeting and self._task:
                await asyncio.sleep(0.5)
                logger.error(f"Greeting: {self._greeting}")
                await self._task.queue_frame(TTSSpeakFrame(self._greeting))

        @self._transport.event_handler("on_participant_disconnected")
        async def _left(_, __):
            if self._task:
                await self._task.cancel()

    async def start(self) -> None:
        """Build and run the pipeline."""
        if self._task is None or self._runner is None:
            await self._build_task()
        await self._runner.run(self._task)  # type: ignore[arg-type]
