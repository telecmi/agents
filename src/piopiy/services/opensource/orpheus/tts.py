import asyncio
import json
import logging
import time
import uuid
from typing import AsyncGenerator, Optional, Dict, Any
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from loguru import logger
from pydantic import BaseModel

from piopiy.frames.frames import (
    Frame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    ErrorFrame,
    StartInterruptionFrame
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.ai_services import TTSService
from piopiy.transcriptions.language import Language
from piopiy.utils.tracing.service_decorators import traced_tts


class OrpheusTTSService(TTSService):
    """Text-to-Speech service using Orpheus WebSocket server.
    
    This service connects to an Orpheus TTS WebSocket server to generate speech.
    """
    
    class InputParams(BaseModel):
        """Configuration parameters for Orpheus TTS service."""
        language: Optional[Language] = Language.EN
        temperature: Optional[float] = 0.7
        top_p: Optional[float] = 0.9
        max_tokens: Optional[int] = 4096

    def __init__(
        self,
        *,
        server_url: str = "ws://localhost:60007",
        api_key: str = "telecmi@123",
        voice: Optional[str] = None,
        sample_rate: Optional[int] = 24000,
        connection_timeout: float = 10.0,
        params: InputParams = InputParams(),
        **kwargs,
    ):
        """Initialize Orpheus TTS service.
        
        Args:
            server_url: WebSocket URL of the Orpheus TTS server
            api_key: API key for authentication
            voice: Voice ID to use (optional)
            sample_rate: Output audio sample rate
            connection_timeout: Timeout for WebSocket connections
            params: Additional configuration parameters
        """
        super().__init__(sample_rate=sample_rate, **kwargs)
        
        self.server_url = server_url
        self.api_key = api_key
        self.voice = voice
        self.connection_timeout = connection_timeout
        
        # Extract settings from params
        self._settings = {
            "language": params.language,
            "temperature": params.temperature,
            "top_p": params.top_p,
            "max_tokens": params.max_tokens
        }
        
        # Connection management
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connection_lock = asyncio.Lock()
        self._active_requests: Dict[str, asyncio.Event] = {}
        
        logger.info(f"Initialized Orpheus TTS service for {server_url}")

    def can_generate_metrics(self) -> bool:
        return True

    async def _ensure_connection(self) -> bool:
        """Ensure WebSocket connection is established"""
        async with self._connection_lock:
            if self._websocket and not self._websocket.closed:
                return True
            
            try:
                logger.info(f"Connecting to Orpheus TTS server at {self.server_url}")
                
                headers = {'Authorization': f'Bearer {self.api_key}'}
                
                self._websocket = await asyncio.wait_for(
                    websockets.connect(
                        self.server_url,
                        extra_headers=headers,
                        max_size=10 * 1024 * 1024,
                        ping_interval=20,
                        ping_timeout=10
                    ),
                    timeout=self.connection_timeout
                )
                
                logger.info("Successfully connected to Orpheus TTS server")
                return True
                
            except Exception as e:
                logger.error(f"Failed to connect to {self.server_url}: {e}")
                return False

    async def _close_connection(self):
        """Close WebSocket connection"""
        async with self._connection_lock:
            if self._websocket and not self._websocket.closed:
                try:
                    await self._websocket.close()
                    logger.info("Closed connection to Orpheus TTS server")
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
                finally:
                    self._websocket = None

    @traced_tts
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Generate speech from text using Orpheus TTS.
        
        Args:
            text: The text to convert to speech
            
        Yields:
            Frames containing audio data and status information.
        """
        logger.debug(f"Generating TTS: [{text}]")
        
        try:
            await self.start_ttfb_metrics()
            yield TTSStartedFrame()
            
            if not await self._ensure_connection():
                yield ErrorFrame("Failed to connect to TTS server")
                return

            request_id = f"req-{uuid.uuid4().hex[:8]}"
            cancel_event = asyncio.Event()
            self._active_requests[request_id] = cancel_event
            
            try:
                # Send TTS request
                payload = {
                    "api_key": self.api_key,
                    "text": text,
                    "voice": self.voice,
                    "sample_rate": self.sample_rate,
                    "temperature": self._settings["temperature"],
                    "top_p": self._settings["top_p"],
                    "max_tokens": self._settings["max_tokens"]
                }
                await self._websocket.send(json.dumps(payload))
                logger.info(f"Sent TTS request: '{text[:50]}...'")
                
                await self.start_tts_usage_metrics(text)
                
                chunk_count = 0
                start_time = time.time()
                started = False
                complete_message = b""
                # Process server responses
                async for message in self._websocket:
                    if cancel_event.is_set():
                        logger.info(f"Request {request_id} cancelled")
                        break
                    
                    if isinstance(message, bytes):
                        # Audio data chunk
                        if not started:
                            started = True
                            logger.info("Started streaming audio from Orpheus")
                        
                        chunk_count += 1
                        logger.debug(f"Received audio chunk {chunk_count} ({len(message)} bytes)")
                        # complete_message = complete_message + message
                        yield TTSAudioRawFrame(
                                audio=message,
                                sample_rate=self.sample_rate,
                                num_channels=1
                            )
                    else:
                        # Control message
                        try:
                            data = json.loads(message)
                            msg_type = data.get('type')
                            
                            if msg_type == 'complete':
                                metrics = data.get('metrics', {})
                                total_time = time.time() - start_time
                                logger.info(f"TTS completed: {chunk_count} chunks in {total_time:.3f}s")
                                break
                            elif msg_type == 'error':
                                error_msg = data.get('message', 'Unknown error')
                                logger.error(f"TTS server error: {error_msg}")
                                yield ErrorFrame(f"TTS error: {error_msg}")
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                yield TTSStoppedFrame()
                
            except ConnectionClosed:
                logger.warning("Connection to TTS server was closed")
                yield ErrorFrame("Connection to TTS server lost")
                
            except WebSocketException as e:
                logger.error(f"WebSocket error during TTS: {e}")
                yield ErrorFrame(f"WebSocket error: {e}")
                
            except Exception as e:
                logger.error(f"TTS generation error: {e}")
                yield ErrorFrame(f"TTS error: {e}")
                
            finally:
                if request_id in self._active_requests:
                    del self._active_requests[request_id]
            
        except Exception as e:
            logger.error(f"{self} exception: {e}")
            yield ErrorFrame(f"Error generating audio: {str(e)}")

    async def _handle_interruption(self, frame: StartInterruptionFrame, direction: FrameDirection):
        """Handle interruption by cancelling active requests"""
        await super()._handle_interruption(frame, direction)
        await self.stop_all_metrics()
        
        # Cancel all active requests
        for request_id, cancel_event in self._active_requests.items():
            cancel_event.set()
            logger.info(f"Cancelled TTS request {request_id} due to interruption")

    async def cleanup(self):
        """Cleanup resources"""
        # Cancel all active requests
        for cancel_event in self._active_requests.values():
            cancel_event.set()
        
        await self._close_connection()
        logger.info("OrpheusTTSService cleanup completed")