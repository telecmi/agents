# Copyright (c) 2024-2026, TeleCMI
# SPDX-License-Identifier: BSD 2-Clause License
"""Backward-compatibility shim for ``SpeechAgent``.

``SpeechAgent`` was a separate orchestrator for speech-to-speech (omni) models
like Gemini Live and OpenAI Realtime. ``VoiceAgent`` now handles both cascaded
(STT → LLM → TTS) and speech-to-speech pipelines via the same API:

    voice = VoiceAgent(instructions=..., greeting=...)
    await voice.configure(llm=gemini_live)   # no `tts` → speech-to-speech
    await voice.start()

This module remains so existing code keeps importing ``SpeechAgent`` and using
``Action(omni=..., tts=PassThroughTTS())`` works unchanged. New code should use
``VoiceAgent`` directly.
"""

from __future__ import annotations

import warnings
from typing import Any, Optional

from piopiy.processors.frame_processor import FrameProcessor
from piopiy.voice_agent import VoiceAgent


class SpeechAgent(VoiceAgent):
    """Deprecated alias of :class:`VoiceAgent` for speech-to-speech models.

    Prefer ``VoiceAgent(...).configure(llm=<realtime_service>)`` (no ``tts``).
    """

    async def Action(
        self,
        *,
        omni: FrameProcessor,
        tts: Optional[FrameProcessor] = None,  # ignored; kept for back-compat
        **kwargs: Any,
    ) -> None:
        """Configure a speech-to-speech pipeline.

        ``omni`` is the realtime model (e.g. ``GeminiLiveLLMService``). ``tts``
        is accepted but ignored — the realtime model emits audio directly, so
        no TTS step is needed. ``PassThroughTTS`` workarounds can be deleted.
        """
        if tts is not None:
            warnings.warn(
                "SpeechAgent.Action(tts=...) is ignored: realtime models emit "
                "audio directly. Drop the tts argument and remove any "
                "PassThroughTTS shim.",
                DeprecationWarning,
                stacklevel=2,
            )
        await self.configure(llm=omni, **kwargs)
