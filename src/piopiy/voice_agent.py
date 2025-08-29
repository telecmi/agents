from __future__ import annotations
import asyncio
from typing import Any, Callable, List, Optional

from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.frames.frames import TextFrame, BotSpeakingFrame, LLMFullResponseEndFrame
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
        tools: Optional[List[Any]] = None,
        mcp_client: Optional[Any] = None,
        greeting: Optional[str] = None,
        idle_timeout_secs: int = 60,
    ) -> None:
        self._instructions = instructions
        self._messages = [{"role": "system", "content": instructions}]
        self._tools = tools or []
        self._mcp_client = mcp_client
        self._greeting = greeting
        self._idle_timeout_secs = idle_timeout_secs

        # components/config set by AgentAction()
        self.transport: Optional[BaseTransport] = None
        self._stt: Optional[FrameProcessor] = None
        self._llm: Optional[FrameProcessor] = None
        self._tts: Optional[FrameProcessor] = None
        self._vad: Optional[FrameProcessor] = None
        self._enable_metrics = False
        self._enable_usage_metrics = False
        self._allow_interruptions = False
        self._interruption_strategy: Optional[BaseInterruptionStrategy] = None

        # runtime fields (must exist to avoid AttributeError)
        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None

    def AgentAction(
        self,
        *,
        stt: FrameProcessor,
        llm: FrameProcessor,
        tts: FrameProcessor,
        vad: Optional[FrameProcessor] = None,  # pass SileroVADAnalyzer() to enable, or None to disable
        enable_metrics: bool = True,
        enable_usage_metrics: bool = True,
        allow_interruptions: bool = True,
        interruption_strategy: Optional[BaseInterruptionStrategy] = None,  # e.g., MinWordsInterruptionStrategy(min_words=1)
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

        # Build transport now (VAD goes into TelecmiParams.vad_analyzer)
        if telecmi_params is None:
            telecmi_params = TelecmiParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                audio_out_sample_rate=24000,
                vad_analyzer=(self._vad if isinstance(self._vad, SileroVADAnalyzer) else None),
            )
        self.transport = TelecmiTransport(params=telecmi_params)

    async def _build_task(self) -> None:
        """Assemble Pipeline + Task (must be awaited before run)."""
        if not (self.transport and self._stt and self._llm and self._tts):
            raise RuntimeError("Call AgentAction(...) before start(). Missing components.")

        transport = self.transport
        processors: List[FrameProcessor] = [transport.input()]

        # NOTE: VAD is typically handled inside TelecmiParams via vad_analyzer.
        # If you also have a standalone VAD processor, you can insert it here:
        # if self._vad and not isinstance(self._vad, SileroVADAnalyzer):
        #     processors.append(self._vad)

        processors.append(self._stt)

        context_aggregator = None
        if OpenAILLMContext and hasattr(self._llm, "create_context_aggregator"):
            ctx = OpenAILLMContext(self._messages)
            context_aggregator = self._llm.create_context_aggregator(ctx)
            processors.append(context_aggregator.user())

        if self._mcp_client:
            await self._mcp_client.register_tools(self._llm)

        if self._tools and hasattr(self._llm, "register_function"):
            for name, handler in self._tools:
                self._llm.register_function(name, handler)

        processors.extend([self._llm, self._tts, transport.output()])
        if context_aggregator:
            processors.append(context_aggregator.assistant())

        pipe = Pipeline(processors)

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

        self._task = PipelineTask(pipe, params=params)
        self._runner = PipelineRunner(handle_sigint=False)

        # events
        @transport.event_handler("on_first_participant_joined")
        async def _greet(_, _pid):
            if self._greeting:
                await asyncio.sleep(1)
                if self._task:
                    if isinstance(self._greeting, str):
                     await self._task.queue_frame(TextFrame(self._greeting))

        @transport.event_handler("on_participant_disconnected")
        async def _left(_, __):
            if self._task:
                await self._task.cancel()

    async def start(self) -> None:
        """Build and run the pipeline."""
        if self._task is None or self._runner is None:
            await self._build_task()
        await self._runner.run(self._task)  # type: ignore[arg-type]
