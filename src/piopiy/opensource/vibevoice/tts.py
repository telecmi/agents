"""
Piopiy TTS Service for VibeVoice WebSocket Server
"""

import os
import json
from typing import AsyncGenerator
from loguru import logger
from dotenv import load_dotenv

import numpy as np
import websockets

from piopiy.frames.frames import (
    Frame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    ErrorFrame,
)
from piopiy.services.tts_service import TTSService

load_dotenv()


class OpenVibeVoiceTTSService(TTSService):
    def __init__(
        self,
        *,
        server_url: str = os.getenv("VIBEVOICE_SERVER_URL"),
        sample_rate: int = 24000,
        num_channels: int = 1,
        **kwargs,
    ):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self._server_url = server_url
        self._num_channels = num_channels
        self._sample_rate = sample_rate

    def can_generate_metrics(self) -> bool:
        return True

    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        logger.debug(f"VibeVoice TTS request: {text[:50]}...")

        try:
            async with websockets.connect(self._server_url) as websocket:
                await websocket.send(json.dumps({"text": text}))
                yield TTSStartedFrame()

                async for message in websocket:
                    if isinstance(message, bytes):
                        audio_array = np.frombuffer(message, dtype=np.float32)
                        audio_int16 = (audio_array * 32767).astype(np.int16)
                        yield TTSAudioRawFrame(
                            audio=audio_int16.tobytes(),
                            sample_rate=self._sample_rate,
                            num_channels=self._num_channels,
                        )
                    else:
                        try:
                            event = json.loads(message)
                            if event.get("event") == "ttft":
                                logger.info(f"VibeVoice TTFT: {event.get('value', 0):.3f}s")
                            elif event.get("event") == "error":
                                err_msg = event.get("message", "Unknown server error")
                                logger.error(f"VibeVoice server error: {err_msg}")
                                yield ErrorFrame(error=err_msg)
                                break
                            elif event.get("event") == "end":
                                logger.debug("VibeVoice TTS complete")
                                break
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON from server: {message}")

                yield TTSStoppedFrame()

        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"WebSocket connection closed: {e}")
            yield ErrorFrame(error=f"WebSocket connection closed: {e}")
            yield TTSStoppedFrame()

        except Exception as e:
            logger.error(f"VibeVoice TTS error: {e}")
            yield ErrorFrame(error=str(e))
            yield TTSStoppedFrame()
