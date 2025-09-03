#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import base64
import json
import uuid
import numpy as np
from typing import AsyncGenerator, List, Optional, Union

from loguru import logger
from pydantic import BaseModel

from piopiy.frames.frames import (
    BotStoppedSpeakingFrame,
    CancelFrame,
    EndFrame,
    ErrorFrame,
    Frame,
    LLMFullResponseEndFrame,
    StartFrame,
    StartInterruptionFrame,
    TTSAudioRawFrame,
    TTSSpeakFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.ai_services import AudioContextWordTTSService, TTSService
from piopiy.services.websocket_service import WebsocketService
from piopiy.transcriptions.language import Language
# from misaki import espeak #pip install misaki
# from misaki.espeak import EspeakG2P

from piopiy.utils.tracing.service_decorators import traced_tts

# See .env.example for Cartesia configuration needed
try:
    import websockets
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error(
        "In order to use Cartesia, you need to `pip install piopiy-ai[cartesia]`. Also, set `CARTESIA_API_KEY` environment variable."
    )
    raise Exception(f"Missing module: {e}")

try:
    from kokoro_onnx import Kokoro
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error(
        "In order to use Kokoro, you need to `pip install kokoro-onnx`. Also, download the model files from the Kokoro repository."
    )
    raise Exception(f"Missing module: {e}")


def language_to_kokoro_language(language: Language) -> Optional[str]:
    """Convert piopiy Language to Kokoro language code."""
    BASE_LANGUAGES = {
        Language.EN: "en-us",
        # Add more language mappings as supported by Kokoro
        Language.HI:"hi",
    }
    
    result = BASE_LANGUAGES.get(language)
    
    # If not found in base languages, try to find the base language from a variant
    if not result:
        lang_str = str(language.value)
        base_code = lang_str.split("-")[0].lower()
        # Look up the base code in our supported languages
        result = f"{base_code}-us" if base_code in ["en"] else None
        
    return result


class KokoroTTSService(TTSService):
    """Text-to-Speech service using Kokoro for on-device TTS.
    
    This service uses Kokoro to generate speech without requiring external API connections.
    """
    
    class InputParams(BaseModel):
        """Configuration parameters for Kokoro TTS service."""
        language: Optional[Language] = Language.EN
        speed: Optional[float] = 1.0

    def __init__(
        self,
        *,
        model_path: str,
        voices_path: str,
        voice_id: str = "af_sarah",
        sample_rate: Optional[int] = None,
        is_phonemes: bool = False,
        params: InputParams = InputParams(),
        **kwargs,
    ):
        """Initialize Kokoro TTS service.
        
        Args:
            model_path: Path to the Kokoro ONNX model file
            voices_path: Path to the Kokoro voices file
            voice_id: ID of the voice to use
            sample_rate: Output audio sample rate
            params: Additional configuration parameters
        """
        super().__init__(sample_rate=sample_rate, **kwargs)
        logger.info(f"Initializing Kokoro TTS service with model_path: {model_path} and voices_path: {voices_path}")
        self._kokoro = Kokoro(model_path, voices_path)
        self.is_phonemes = is_phonemes
        logger.info(f"Kokoro initialized")
        self._settings = {
            "language": self.language_to_service_language(params.language)
            if params.language
            else "en-us",
            "speed": params.speed,
        }
        self.set_voice(voice_id)  # Presumably this sets self._voice_id
        
        logger.info("Kokoro TTS service initialized")

    def can_generate_metrics(self) -> bool:
        return True

    def language_to_service_language(self, language: Language) -> Optional[str]:
        """Convert piopiy language to Kokoro language code."""
        return language_to_kokoro_language(language)

    @traced_tts
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Generate speech from text using Kokoro in a streaming fashion.
        
        Args:
            text: The text to convert to speech
            
        Yields:
            Frames containing audio data and status information.
        """
        logger.debug(f"Generating TTS: [{text}]")
        try:
            await self.start_ttfb_metrics()
            yield TTSStartedFrame()
            
            # Use Kokoro's streaming mode. The create_stream method is assumed to return
            # an async generator that yields (samples, sample_rate) tuples, where samples is a numpy array.
            logger.info(f"Creating stream")
            
            if self._settings["language"] == "hi":

                #phonemizing hindi text will be added
                # g2p = EspeakG2P(language=self._settings["language"])
                # text = "सपने वो नहीं जो हम सोते समय देखते हैं, सपने वो हैं जो हमें सोने नहीं देते।"
                # text, _ = g2p(text)
                # self.is_phonemes = True
                pass

            stream = self._kokoro.create_stream(
                text,
                voice=self._voice_id,
                speed=self._settings["speed"],
                lang=self._settings["language"],
                is_phonemes = self.is_phonemes,
            )

            
            await self.start_tts_usage_metrics(text)
            started = False
            async for samples, sample_rate in stream:
                if not started:
                    started = True
                    logger.info(f"Started streaming")
                # Convert the float32 samples (assumed in the range [-1, 1]) to int16 PCM format
                samples_int16 = (samples * 32767).astype(np.int16)
                yield TTSAudioRawFrame(
                    audio=samples_int16.tobytes(),
                    sample_rate=sample_rate,
                    num_channels=1,
                )
            
            yield TTSStoppedFrame()

        
            
        except Exception as e:
            logger.error(f"{self} exception: {e}")
            yield ErrorFrame(f"Error generating audio: {str(e)}")

    async def _handle_interruption(self, frame: StartInterruptionFrame, direction: FrameDirection):
        await super()._handle_interruption(frame, direction)
        await self.stop_all_metrics()
        # if self._context_id:
        #     cancel_msg = json.dumps({"context_id": self._context_id, "cancel": True})
        #     await self._get_websocket().send(cancel_msg)
        #     self._context_id = None