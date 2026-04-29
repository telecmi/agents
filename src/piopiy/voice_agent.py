# Copyright (c) 2024-2026, TeleCMI
# SPDX-License-Identifier: BSD 2-Clause License

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Mapping, Optional

from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy.adapters.schemas.tools_schema import ToolsSchema
from piopiy.audio.interruptions.base_interruption_strategy import BaseInterruptionStrategy
from piopiy.audio.interruptions.min_words_interruption_strategy import (
    MinWordsInterruptionStrategy,
)
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.vad.vad_analyzer import VADParams
from piopiy.frames.frames import (
    BotSpeakingFrame,
    LLMFullResponseEndFrame,
    LLMRunFrame,
    ManuallySwitchServiceFrame,
    TTSSpeakFrame,
)
from piopiy.pipeline.pipeline import Pipeline
from piopiy.pipeline.runner import PipelineRunner
from piopiy.pipeline.service_switcher import ServiceSwitcher
from piopiy.pipeline.task import PipelineParams, PipelineTask
from piopiy.processors.aggregators.llm_context import LLMContext
from piopiy.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from piopiy.processors.frame_processor import FrameProcessor
from piopiy.transports.services.telecmi import TelecmiParams, TelecmiTransport
from piopiy.turns.user_start.min_words_user_turn_start_strategy import (
    MinWordsUserTurnStartStrategy,
)
from piopiy.turns.user_turn_strategies import UserTurnStrategies

logger = logging.getLogger(__name__)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _map_vad_params(own: Mapping[str, Any]) -> Dict[str, Any]:
    """Map public VAD config keys to Silero analyzer kwargs.

    Public keys (anything else is ignored):
        confidence: 0..1   (default 0.7)  → speech_threshold
        start_secs: float  (default 0.2)  → min_speech_duration_ms
        stop_secs:  float  (default 0.2)  → min_silence_duration_ms
        min_volume: 0..1   (default 0.6)  → volume_threshold
    """
    confidence = _clamp(float(own.get("confidence", 0.7)), 0.0, 1.0)
    start_secs = max(0.0, float(own.get("start_secs", 0.2)))
    stop_secs = max(0.0, float(own.get("stop_secs", 0.2)))
    min_volume = _clamp(float(own.get("min_volume", 0.6)), 0.0, 1.0)
    return {
        "speech_threshold": confidence,
        "min_speech_duration_ms": int(start_secs * 1000),
        "min_silence_duration_ms": int(stop_secs * 1000),
        "volume_threshold": min_volume,
    }


def _build_vad(vad: Any) -> Optional[SileroVADAnalyzer]:
    if vad is None or vad is False:
        return None
    if isinstance(vad, SileroVADAnalyzer):
        return vad
    if isinstance(vad, FrameProcessor):
        return vad  # type: ignore[return-value]
    if isinstance(vad, dict):
        return SileroVADAnalyzer(params=VADParams(**_map_vad_params(vad)))
    if isinstance(vad, bool) and vad:
        return SileroVADAnalyzer()
    return None


class VoiceAgent:
    """Unified voice agent for cascaded, speech-to-speech, and hybrid pipelines.

    Cascaded mode (STT → LLM → TTS):
        await va.configure(stt=stt, llm=llm, tts=tts, vad=True)

    Speech-to-speech mode (realtime model owns audio I/O, e.g. Gemini Live,
    OpenAI Realtime, AWS Nova Sonic, Grok Realtime):
        await va.configure(llm=gemini_live)

    Audio-LLM hybrid (model does ASR internally but emits text; you supply TTS,
    e.g. Ultravox, VibeVoice):
        await va.configure(llm=ultravox, tts=cartesia_tts)

    Mode is detected from the arguments:
        - ``stt`` provided   → cascaded pipeline
        - no ``stt``         → audio-LLM pipeline (with or without an external TTS)
    """

    def __init__(
        self,
        *,
        instructions: str,
        greeting: Optional[str] = None,
        tools: Optional[List[FunctionSchema]] = None,
        idle_timeout_secs: int = 60,
    ) -> None:
        self._instructions = instructions
        self._greeting = greeting
        self._tools = tools or []
        self._idle_timeout_secs = idle_timeout_secs

        self._tool_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self._tool_schemas: Dict[str, FunctionSchema] = {}

        self._stt: Optional[FrameProcessor] = None
        self._llm: Optional[FrameProcessor] = None
        self._tts: Optional[FrameProcessor] = None
        self._stt_switcher: Optional[ServiceSwitcher] = None
        self._tts_switcher: Optional[ServiceSwitcher] = None
        self._mcp_client: Any = None

        self._vad: Optional[SileroVADAnalyzer] = None
        self._enable_metrics = True
        self._enable_usage_metrics = True
        self._allow_interruptions = True
        self._interruption_strategy: Optional[BaseInterruptionStrategy] = None

        self._transport: Optional[TelecmiTransport] = None
        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None
        self._pipe: Optional[Pipeline] = None
        self._processors: List[FrameProcessor] = []

        self.context_aggregator: Optional[LLMContextAggregatorPair] = None

    # ------------------------------------------------------------------ tools

    def add_tool(
        self,
        schema: FunctionSchema,
        handler: Callable[..., Awaitable[Any]],
    ) -> None:
        self._tool_schemas[schema.name] = schema
        self._tool_handlers[schema.name] = handler

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Awaitable[Any]],
    ) -> None:
        self._tool_handlers[name] = handler

    async def switch_service(self, service: FrameProcessor) -> None:
        """Swap a service (typically STT or TTS) at runtime."""
        if self._task:
            await self._task.queue_frame(ManuallySwitchServiceFrame(service=service))

    # ------------------------------------------------------------- configure

    async def configure(
        self,
        *,
        llm: FrameProcessor,
        stt: Optional[FrameProcessor] = None,
        tts: Optional[FrameProcessor] = None,
        stt_switcher: Optional[ServiceSwitcher] = None,
        tts_switcher: Optional[ServiceSwitcher] = None,
        mcp_tools: Optional[Any] = None,
        vad: Optional[Any] = None,
        enable_metrics: bool = True,
        enable_usage_metrics: bool = True,
        allow_interruptions: bool = True,
        interruption_strategy: Optional[BaseInterruptionStrategy] = None,
        telecmi_params: Optional[TelecmiParams] = None,
    ) -> None:
        """Configure the pipeline; the actual pipeline is built in ``start()``.

        Args:
            llm: REQUIRED. Either a cascaded LLM service (e.g. ``OpenAILLMService``)
                or a realtime/speech-to-speech model (e.g. ``GeminiLiveLLMService``,
                ``OpenAIRealtimeLLMService``).
            stt: Required for cascaded mode; omit for speech-to-speech.
            tts: Required for cascaded mode; **omit for speech-to-speech**. The
                presence/absence of this argument is what selects the mode.
            stt_switcher / tts_switcher: ``ServiceSwitcher`` instances for
                runtime provider swapping. Use instead of ``stt`` / ``tts``.
            mcp_tools: An MCP client/tools object to wire into the LLM context.
            vad: One of ``True``, ``False``, ``None``, a ``dict`` of public VAD
                params (``confidence``, ``start_secs``, ``stop_secs``,
                ``min_volume``), or a pre-built ``SileroVADAnalyzer``. For S2S
                models, server-side VAD is normally enough; pass a value here
                only if you also want client-side VAD.
        """
        self._llm = llm
        self._stt = stt
        self._tts = tts
        self._stt_switcher = stt_switcher
        self._tts_switcher = tts_switcher
        self._mcp_client = mcp_tools
        self._enable_metrics = enable_metrics
        self._enable_usage_metrics = enable_usage_metrics
        self._allow_interruptions = allow_interruptions
        self._interruption_strategy = interruption_strategy
        self._vad = _build_vad(vad)

        if telecmi_params is None:
            telecmi_params = TelecmiParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                audio_in_sample_rate=16000,
                audio_out_sample_rate=24000,
            )
        # VAD analyzer lives on the transport in this codebase. (When this SDK
        # cuts over to pipecat 1.1 directly, this will move to
        # ``LLMUserAggregatorParams(vad_analyzer=...)`` and the field on the
        # transport will be removed.)
        setattr(telecmi_params, "vad_analyzer", self._vad)
        self._transport = TelecmiTransport(params=telecmi_params)

    # Backward-compat alias: prefer ``configure()`` going forward.
    async def Action(self, **kwargs: Any) -> None:
        """Deprecated. Use :py:meth:`configure` instead."""
        await self.configure(**kwargs)

    # --------------------------------------------------------------- private

    @property
    def _has_stt(self) -> bool:
        return self._stt is not None or self._stt_switcher is not None

    @property
    def _has_tts(self) -> bool:
        return self._tts is not None or self._tts_switcher is not None

    @property
    def _is_speech_to_speech(self) -> bool:
        """True for pure S2S (no STT, no TTS — the model owns both ends)."""
        return not self._has_stt and not self._has_tts

    def _register_tools_on_llm(self, tool_schemas: List[FunctionSchema]) -> None:
        if not self._tool_handlers:
            return
        by_name = {s.name: s for s in tool_schemas}
        if hasattr(self._llm, "register_function"):
            for name, fn in self._tool_handlers.items():
                try:
                    self._llm.register_function(name, fn)  # type: ignore[union-attr]
                except TypeError:
                    schema = by_name.get(name)
                    if schema:
                        self._llm.register_function(schema, fn)  # type: ignore[union-attr]
        elif hasattr(self._llm, "register_tool"):
            for name, fn in self._tool_handlers.items():
                try:
                    self._llm.register_tool(name, fn)  # type: ignore[union-attr]
                except TypeError:
                    schema = by_name.get(name)
                    if schema:
                        self._llm.register_tool(schema, fn)  # type: ignore[union-attr]
        else:
            raise RuntimeError(
                "LLM service does not expose register_function or register_tool"
            )

    async def _build_task(self) -> None:
        if self._transport is None:
            raise RuntimeError("Call configure(...) first.")
        if self._llm is None:
            raise RuntimeError("Missing llm. Call configure(...).")

        cascaded = self._has_stt
        s2s = self._is_speech_to_speech  # no STT, no TTS — model handles both
        # else: audio-LLM hybrid (model does ASR; external TTS for output)

        # System prompt + greeting handling. Cascaded mode plays the greeting
        # via the TTS service after the participant joins (TTSSpeakFrame). For
        # any audio-in mode (S2S or hybrid) the greeting must come from the
        # model itself, so we inject it as a user instruction in the context.
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._instructions}
        ]
        if not cascaded and self._greeting:
            messages.append(
                {
                    "role": "user",
                    "content": f"Begin the call by saying exactly: {self._greeting!r}",
                }
            )

        # Build the tools schema once, including any tools registered via add_tool.
        tool_schemas: List[FunctionSchema] = list(self._tool_schemas.values())
        if self._tools:
            existing = {s.name for s in tool_schemas}
            tool_schemas.extend(s for s in self._tools if s.name not in existing)
        tools_schema = (
            ToolsSchema(standard_tools=tool_schemas) if tool_schemas else None
        )

        # MCP tools take precedence over the static schema if provided.
        if self._mcp_client is not None:
            ctx = LLMContext(messages, tools=self._mcp_client)
        elif tools_schema is not None:
            ctx = LLMContext(messages, tools_schema)
        else:
            ctx = LLMContext(messages)

        # User turn strategies: only inject the default min-words start strategy
        # for cascaded mode; audio-in models drive their own turn-taking.
        if cascaded and self._allow_interruptions:
            user_turn_strategies = UserTurnStrategies(
                start=[
                    self._interruption_strategy
                    or MinWordsUserTurnStartStrategy(min_words=1)
                ]
            )
        else:
            user_turn_strategies = UserTurnStrategies()

        user_params = LLMUserAggregatorParams(user_turn_strategies=user_turn_strategies)
        self.context_aggregator = LLMContextAggregatorPair(ctx, user_params=user_params)

        self._register_tools_on_llm(tool_schemas)

        tts_proc = self._tts_switcher or self._tts

        if cascaded:
            # input → stt → user_agg → llm → tts → output → assistant_agg
            stt_proc = self._stt_switcher or self._stt
            self._processors = [
                self._transport.input(),
                stt_proc,
                self.context_aggregator.user(),
                self._llm,
                tts_proc,
                self._transport.output(),
                self.context_aggregator.assistant(),
            ]
        else:
            # Audio-in model. TTS is appended only when present (hybrid case).
            # input → user_agg → llm [→ tts] → output → assistant_agg
            self._processors = [
                self._transport.input(),
                self.context_aggregator.user(),
                self._llm,
                *([tts_proc] if self._has_tts else []),
                self._transport.output(),
                self.context_aggregator.assistant(),
            ]

        self._pipe = Pipeline(self._processors)

        params = PipelineParams(
            enable_metrics=self._enable_metrics,
            enable_usage_metrics=self._enable_usage_metrics,
            allow_interruptions=self._allow_interruptions,
        )

        self._task = PipelineTask(
            self._pipe,
            params=params,
            idle_timeout_secs=self._idle_timeout_secs,
            idle_timeout_frames=(BotSpeakingFrame, LLMFullResponseEndFrame),
            cancel_on_idle_timeout=True,
        )
        self._runner = PipelineRunner(handle_sigint=False)

        @self._transport.event_handler("on_first_participant_joined")
        async def _greet(_transport: Any, _participant_id: Any) -> None:
            if not self._task:
                return
            await asyncio.sleep(0.5)
            if cascaded and self._greeting:
                # TTS service speaks the greeting verbatim.
                logger.info("Greeting: %s", self._greeting)
                await self._task.queue_frame(TTSSpeakFrame(self._greeting))
            else:
                # Audio-in model: kick the run; greeting (if any) is in context.
                logger.info("Starting audio-LLM session")
                await self._task.queue_frame(LLMRunFrame())

        @self._transport.event_handler("on_participant_disconnected")
        async def _left(_transport: Any, _participant_id: Any) -> None:
            if self._task:
                await self._task.cancel()

    async def start(self) -> None:
        if self._task is None or self._runner is None:
            await self._build_task()
        await self._runner.run(self._task)  # type: ignore[arg-type]
