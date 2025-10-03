# speech_agent.py
from __future__ import annotations
import asyncio
from asyncio.log import logger
from typing import Any, Mapping, Dict, Optional, List

from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.vad.vad_analyzer import VADParams
from piopiy.frames.frames import TTSSpeakFrame, BotSpeakingFrame, LLMFullResponseEndFrame
from piopiy.pipeline.pipeline import Pipeline
from piopiy.pipeline.runner import PipelineRunner
from piopiy.pipeline.task import PipelineParams, PipelineTask
from piopiy.processors.frame_processor import FrameProcessor
from piopiy.audio.interruptions.base_interruption_strategy import BaseInterruptionStrategy
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.transports.services.telecmi import TelecmiParams, TelecmiTransport

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def _map_vad_params(own: Mapping[str, Any]) -> Dict[str, Any]:
    # public → silero params
    confidence = float(_clamp(float(own.get("confidence", 0.7)), 0.0, 1.0))
    start_secs = max(0.0, float(own.get("start_secs", 0.2)))
    stop_secs  = max(0.0, float(own.get("stop_secs", 0.8)))
    min_volume = float(_clamp(float(own.get("min_volume", 0.6)), 0.0, 1.0))
    return {
        "speech_threshold": confidence,
        "min_speech_duration_ms": int(start_secs * 1000),
        "min_silence_duration_ms": int(stop_secs * 1000),
        "volume_threshold": min_volume,
    }

class SpeechAgent:
    """
    Vendor-neutral voice pipeline:

        TeleCMI.input()
          → model     (audio-in → understanding/decisions; owns tools/memory)
          → tts
          → TeleCMI.output()

    No 'LLM' dependency. 'model' is any FrameProcessor that consumes audio frames
    and yields agent responses (could be Ultravox, Voxtral, Step-Audio, etc.).
    """

    def __init__(self, *, greeting: Optional[str] = None, instructions: str, idle_timeout_secs: int = 60) -> None:
        self._greeting = greeting
        self._idle_timeout_secs = idle_timeout_secs

        self._transport: Optional[TelecmiTransport] = None
        self._model: Optional[FrameProcessor] = None
        self._tts: Optional[FrameProcessor] = None

        self._vad: Optional[SileroVADAnalyzer] = None
        self._enable_metrics = False
        self._enable_usage_metrics = False
        self._allow_interruptions = False
        self._interruption_strategy: Optional[BaseInterruptionStrategy] = None

        self._task: Optional[PipelineTask] = None
        self._runner: Optional[PipelineRunner] = None
        self._processors: List[FrameProcessor] = []
        self._pipe: Optional[Pipeline] = None

    async def Action(
        self,
        *,
        omni: FrameProcessor,                  # REQUIRED: your realtime voice model
        tts: FrameProcessor,                    # REQUIRED: your TTS processor
        telecmi_params: Optional[TelecmiParams] = None,
        vad: Optional[Any] = None,              # True | dict | SileroVADAnalyzer | None
        enable_metrics: bool = True,
        enable_usage_metrics: bool = True,
        allow_interruptions: bool = True,
        interruption_strategy: Optional[BaseInterruptionStrategy] = None,
    ) -> None:
        self._model = omni
        self._tts = tts
        self._enable_metrics = enable_metrics
        self._enable_usage_metrics = enable_usage_metrics
        self._allow_interruptions = allow_interruptions
        self._interruption_strategy = interruption_strategy

        # VAD wiring (optional)
        if isinstance(vad, SileroVADAnalyzer) or isinstance(vad, FrameProcessor):
            self._vad = vad  # type: ignore[assignment]
        elif isinstance(vad, dict):
            self._vad = SileroVADAnalyzer(params=VADParams(**_map_vad_params(vad)))
        elif isinstance(vad, bool) and vad:
            self._vad = SileroVADAnalyzer()
        else:
            self._vad = None

        # TeleCMI transport
        telecmi_params = telecmi_params or TelecmiParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
        )
        # attach VAD if available
        setattr(telecmi_params, "vad_analyzer", self._vad)
        self._transport = TelecmiTransport(params=telecmi_params)

    async def _build_task(self) -> None:
        if not (self._transport and self._model and self._tts):
            raise RuntimeError("configure(...) first with model, tts, telecmi_params")

        self._processors = [
            self._transport.input(),
            self._model,           # ← owns tool-calls & memory strategy internally
            self._tts,
            self._transport.output(),
        ]
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
        await self._runner.run(self._task)
