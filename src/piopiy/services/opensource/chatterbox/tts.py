#
# Copyright (c) 2024–2025, TeleCMI
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import numpy as np
import asyncio
from typing import AsyncGenerator, Optional

from loguru import logger

from piopiy.frames.frames import (
    ErrorFrame,
    Frame,
    StartInterruptionFrame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.ai_services import TTSService
from piopiy.transcriptions.language import Language
from piopiy.utils.tracing.service_decorators import traced_tts

try:
    from chatterbox.tts import ChatterboxTTS
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    raise Exception(f"Missing module: {e}")


def language_to_chatterbox_language(language: Language) -> Optional[str]:
    """Convert piopiy Language to Chatterbox language code."""
    BASE_LANGUAGES = {
        Language.EN: "en-us",
        Language.HI: "hi",
    }
    
    result = BASE_LANGUAGES.get(language)
    
    if not result:
        lang_str = str(language.value)
        base_code = lang_str.split("-")[0].lower()
        result = f"{base_code}-us" if base_code in ["en"] else None
        
    return result


class ChatterboxTTSService(TTSService):
    # CLASS-LEVEL SHARED MODEL - This is the key change!
    _shared_model: Optional[ChatterboxTTS] = None
    _model_lock = asyncio.Lock()
    _model_device = None
    
    def __init__(
        self,
        *,
        voice_path: str,
        device: str = "cuda",
        sample_rate: Optional[int] = 24000,
        **kwargs,
    ):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self.device = device
        self.voice_path = voice_path
        
        # Instance-specific locks for streaming
        self._stream_lock = asyncio.Lock()
        self._current_stream = None
        self._is_streaming = False
        self._session_id = id(self)
        self.warm_up_model()
        logger.info(f"ChatterboxTTSService instance created (session {self._session_id})")

        
    def warm_up_model(self):
        text_list =["hello i am from telecmi",
                    "today is monday"]
        for i in text_list:
            self.run_tts(i)

    @classmethod
    async def _ensure_shared_model_loaded(cls, device: str) -> ChatterboxTTS:
        """Load the model once and share it across all instances"""
        # If model already loaded on the same device, return it
        if cls._shared_model is not None and cls._model_device == device:
            logger.debug(f"Using existing shared model on {device}")
            return cls._shared_model
        
        # Load model with lock to prevent multiple simultaneous loads
        async with cls._model_lock:
            # Double-check after acquiring lock
            if cls._shared_model is not None and cls._model_device == device:
                return cls._shared_model
            
            # If device changed or model not loaded, load it
            logger.info(f"Loading shared Chatterbox model on {device} (one-time operation)")
            try:
                # Load the model asynchronously
                model = await ChatterboxTTS.from_pretrained_async(device)
                if model is None:
                    raise RuntimeError("Failed to load Chatterbox model")
                
                cls._shared_model = model
                cls._model_device = device
                logger.info(f"Shared Chatterbox model loaded successfully on {device}")
                return cls._shared_model
                
            except Exception as e:
                logger.error(f"Failed to load shared model: {e}")
                raise
    
    async def _get_model(self) -> ChatterboxTTS:
        """Get the shared model instance"""
        return await self._ensure_shared_model_loaded(self.device)
    
    def can_generate_metrics(self) -> bool:
        return True
    
    async def _cleanup_stream(self):
        """Clean up the current stream for this session"""
        async with self._stream_lock:
            if self._current_stream:
                try:
                    if hasattr(self._current_stream, 'aclose'):
                        await self._current_stream.aclose()
                except Exception as e:
                    logger.debug(f"Session {self._session_id}: Error cleaning up stream: {e}")
                finally:
                    self._current_stream = None
                    self._is_streaming = False

    @traced_tts
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Generate speech from text using Chatterbox in a streaming fashion."""
        # Clean up any previous stream for this session
        await self._cleanup_stream()
        
        # Get the shared model
        model = await self._get_model()
        
        logger.debug(f"Session {self._session_id}: Generating TTS: [{text[:50]}...]")
        
        # Use instance-specific lock for streaming
        async with self._stream_lock:
            self._is_streaming = True
            
            try:
                await self.start_ttfb_metrics()
                yield TTSStartedFrame()
                
                logger.info(f"Session {self._session_id}: Creating stream")
                
                # Create a new stream for this specific request using the shared model
                self._current_stream = model.create_stream(text, self.voice_path)
                
                await self.start_tts_usage_metrics(text)
                started = False
                
                async for samples, sample_rate in self._current_stream:
                    # Check if this specific session should stop streaming
                    if not self._is_streaming:
                        logger.info(f"Session {self._session_id}: Streaming interrupted")
                        break
                    
                    if not started:
                        started = True
                        logger.debug(f"Session {self._session_id}: Started streaming audio")
                    
                    samples_int16 = (samples * 32767).astype(np.int16)
                    yield TTSAudioRawFrame(
                        audio=samples_int16.tobytes(),
                        sample_rate=sample_rate,
                        num_channels=1,
                    )
                
                yield TTSStoppedFrame()
                logger.debug(f"Session {self._session_id}: TTS streaming completed")
                
            except asyncio.CancelledError:
                logger.info(f"Session {self._session_id}: TTS streaming cancelled")
                yield TTSStoppedFrame()
                raise
            except Exception as e:
                logger.error(f"Session {self._session_id} exception: {e}")
                yield ErrorFrame(f"Error generating audio: {str(e)}")
            finally:
                self._is_streaming = False
                self._current_stream = None

    async def _handle_interruption(self, frame: StartInterruptionFrame, direction: FrameDirection):
        """Handle interruptions by stopping the current stream for this session"""
        logger.info(f"Session {self._session_id}: Handling TTS interruption")
        
        # Stop the current stream for this session only
        async with self._stream_lock:
            self._is_streaming = False
        
        await super()._handle_interruption(frame, direction)
        await self.stop_all_metrics()
    
    async def cleanup(self):
        """Cleanup method for this service instance"""
        await self._cleanup_stream()
        logger.info(f"Session {self._session_id}: ChatterboxTTSService instance cleaned up")
    
    @classmethod
    async def cleanup_shared_model(cls):
        """
        Optional: Call this to explicitly clean up the shared model.
        Useful for graceful shutdown.
        """
        async with cls._model_lock:
            if cls._shared_model:
                logger.info("Cleaning up shared Chatterbox model")
                cls._shared_model = None
                cls._model_device = None