from __future__ import annotations
import asyncio
from asyncio.log import logger
from typing import Any, Awaitable, Callable, List, Optional, Mapping, Dict
import math


from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy.adapters.schemas.tools_schema import ToolsSchema
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.vad.vad_analyzer import VADParams
from piopiy.frames.frames import TTSSpeakFrame, BotSpeakingFrame, LLMFullResponseEndFrame
from piopiy.pipeline.pipeline import Pipeline
from piopiy.pipeline.runner import PipelineRunner
from piopiy.pipeline.task import PipelineParams, PipelineTask
from piopiy.processors.frame_processor import FrameProcessor
from piopiy.audio.interruptions.base_interruption_strategy import BaseInterruptionStrategy
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.transports.base_transport import BaseTransport
from piopiy.transports.services.telecmi import TelecmiParams, TelecmiTransport
from piopiy.audio.filters.krisp_viva_filter import KrispVivaFilter

try:
    from piopiy.processors.aggregators.openai_llm_context import OpenAILLMContext
except Exception:
    OpenAILLMContext = None  # type: ignore


# --- NEW: map your public VAD config -> Silero kwargs -------------------------
def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def map_vad_params(own: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Accept ONLY these public keys (others are ignored/forbidden):
      - confidence: 0..1 (default 0.7)  → maps to `speech_threshold`
      - start_secs: float (default 0.2) → maps to `min_speech_duration_ms` (sec→ms)
      - stop_secs:  float (default 0.8) → maps to `min_silence_duration_ms` (sec→ms)
      - min_volume: 0..1 (default 0.6)  → maps to `volume_threshold`
    """
    # defaults
    confidence = 0.7
    start_secs = 0.2
    stop_secs  = 0.8
    min_volume = 0.6

    # pull + clamp
    if "confidence" in own:
        try:
            confidence = _clamp(float(own["confidence"]), 0.0, 1.0)
        except (TypeError, ValueError):
            confidence = 0.7

    if "start_secs" in own:
        try:
            start_secs = max(0.0, float(own["start_secs"]))
        except (TypeError, ValueError):
            start_secs = 0.2

    if "stop_secs" in own:
        try:
            stop_secs = max(0.0, float(own["stop_secs"]))
        except (TypeError, ValueError):
            stop_secs = 0.8

    if "min_volume" in own:
        try:
            min_volume = _clamp(float(own["min_volume"]), 0.0, 1.0)
        except (TypeError, ValueError):
            min_volume = 0.6

    # map to Silero analyzer kwargs (use names that are widely supported)
    mapped: Dict[str, Any] = {
        "speech_threshold": confidence,
        "min_speech_duration_ms": int(start_secs * 1000.0),
        "min_silence_duration_ms": int(stop_secs * 1000.0),
        "volume_threshold": min_volume,
    }

    return mapped

# -----------------------------------------------------------------------------

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
        self._tools = tools or []
        self._greeting = greeting
        self._idle_timeout_secs = idle_timeout_secs

        self._tool_handlers: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._tool_schemas: dict[str, FunctionSchema] = {}

        self._transport: Optional[BaseTransport] = None
        self._stt: Optional[FrameProcessor] = None
        self._llm: Optional[FrameProcessor] = None
        self._tts: Optional[FrameProcessor] = None
        self._vad: Optional[SileroVADAnalyzer] = None  # analyzer object we’ll inject
        self.audio_filter: Optional[KrispVivaFilter] = None

        self._enable_metrics = False
        self._enable_usage_metrics = False
        self._allow_interruptions = False
        self._interruption_strategy: Optional[BaseInterruptionStrategy] = None

        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None
        self.context_aggregator = None
        self._processors: List[FrameProcessor] = []
        self._pipe: Optional[Pipeline] = None

    # ---- Tool APIs ----
    def add_tool(self, schema: FunctionSchema, handler: Callable[..., Awaitable[Any]]) -> None:
        self._tool_schemas[schema.name] = schema
        self._tool_handlers[schema.name] = handler

    def register_tool(self, name: str, handler: Callable[..., Awaitable[Any]]) -> None:
        self._tool_handlers[name] = handler

    # ---- Configuration ----
    async def Action(
        self,
        *,
        stt: FrameProcessor,
        llm: FrameProcessor,
        tts: FrameProcessor,
        mcp_tools: Optional[Any] = None,
        # NEW: flexible VAD arg. Accepts:
        #   - True  -> enable with library defaults
        #   - dict  -> enable with your public keys (mapped internally)
        #   - SileroVADAnalyzer/FrameProcessor -> back-compat: use as-is
        #   - None/False -> disabled
        vad: Optional[Any] = None,
        enable_metrics: bool = True,
        enable_usage_metrics: bool = True,
        allow_interruptions: bool = True,
        interruption_strategy: Optional[BaseInterruptionStrategy] = None,
        telecmi_params: Optional[TelecmiParams] = None,
        #  ADD THIS PARAMETER:
        enable_krisp: bool = False,
        krisp_model_path: Optional[str] = None,
        krisp_suppression_level: int = 30,
    ) -> None:
        """Store components and toggles; pipeline is built in start()."""
        self._stt = stt
        self._llm = llm
        self._tts = tts
        self._enable_metrics = enable_metrics
        self._enable_usage_metrics = enable_usage_metrics
        self._allow_interruptions = allow_interruptions
        self._interruption_strategy = interruption_strategy
        self._mcp_client = mcp_tools or None
            
        # --- NEW: Build VAD analyzer from bool/dict or keep existing analyzer
        self._vad = None
        if isinstance(vad, SileroVADAnalyzer) or isinstance(vad, FrameProcessor):
            # back-compat: a ready analyzer/processor was passed in
            self._vad = vad  # type: ignore[assignment]
        elif isinstance(vad, dict):
            # your public config -> Silero kwargs
            silero_kwargs = map_vad_params(vad)
            self._vad = SileroVADAnalyzer(params=VADParams(**silero_kwargs))
        elif isinstance(vad, bool) and vad:
            # simple on-switch with library defaults
            self._vad = SileroVADAnalyzer()
        # else: None/False => leave disabled

        # ADD KRISP FILTER INITIALIZATION:
        if enable_krisp:   
            self.audio_filter = KrispVivaFilter(
                model_path=krisp_model_path,
                noise_suppression_level=krisp_suppression_level
            )
        else:
            self.audio_filter = None

        # Build transport (VAD goes into TelecmiParams.vad_analyzer)
        if telecmi_params is None:
            telecmi_params = TelecmiParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                audio_out_sample_rate=24000,
                audio_in_sample_rate=16000,
            )

        # ADD FILTER TO TRANSPORT:
        if self.audio_filter:
            telecmi_params.audio_in_filter = self.audio_filter

        # Inject analyzer (attribute may or may not exist; be defensive)
        try:
            telecmi_params.vad_analyzer = self._vad  # type: ignore[attr-defined]
        except Exception:
            # Fallback: setattr so we don't crash on dataclass variants
            setattr(telecmi_params, "vad_analyzer", self._vad)

        self._transport = TelecmiTransport(params=telecmi_params)

    # ---- Pipeline build & run ----
    async def _build_task(self) -> None:
        if not (self._transport and self._stt and self._llm and self._tts):
            raise RuntimeError("Call AgentAction(...) before start(). Missing components.")

        self._processors = [self._transport.input(), self._stt]

        tool_schemas: List[FunctionSchema] = list(self._tool_schemas.values())
        if self._tools:
            names = {s.name for s in tool_schemas}
            tool_schemas.extend([s for s in self._tools if s.name not in names])

        if OpenAILLMContext and hasattr(self._llm, "create_context_aggregator"):
            tools_schema = ToolsSchema(standard_tools=tool_schemas) if tool_schemas else None
            ctx = OpenAILLMContext(self._messages, tools_schema) if tools_schema else OpenAILLMContext(self._messages)
            if self._mcp_client:
                ctx = OpenAILLMContext(self._messages, tools=self._mcp_client) if self._mcp_client else OpenAILLMContext(self._messages)
            self.context_aggregator = self._llm.create_context_aggregator(ctx)
            self._processors.append(self.context_aggregator.user())

        by_name = {s.name: s for s in tool_schemas}

        if hasattr(self._llm, "register_function"):
            for name, fn in self._tool_handlers.items():
                try:
                    self._llm.register_function(name, fn)
                except TypeError:
                    schema = by_name.get(name)
                    if schema:
                        self._llm.register_function(schema, fn)
        elif hasattr(self._llm, "register_tool"):
            for name, fn in self._tool_handlers.items():
                try:
                    self._llm.register_tool(name, fn)
                except TypeError:
                    schema = by_name.get(name)
                    if schema:
                        self._llm.register_tool(schema, fn)
        else:
            raise RuntimeError("LLMService missing register_function/register_tool")

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
        if self._task is None or self._runner is None:
            await self._build_task()
        await self._runner.run(self._task)  # type: ignore[arg-type]
