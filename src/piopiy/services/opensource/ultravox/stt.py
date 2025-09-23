#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ultravox speech-to-text service implementation for piopiy pipeline."""

import asyncio
import base64
import json
import time
import uuid
from typing import AsyncGenerator, Optional, Dict, Any
from urllib.parse import urlparse

import websockets
from loguru import logger
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK

from piopiy.frames.frames import (
    CancelFrame,
    EndFrame,
    ErrorFrame,
    Frame,
    InterimTranscriptionFrame,
    StartFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.stt_service import STTService
from piopiy.transcriptions.language import Language
from piopiy.utils.time import time_now_iso8601
from piopiy.utils.tracing.service_decorators import traced_stt


class UltravoxSTTService(STTService):
    """Ultravox speech-to-text service.

    Provides speech recognition using an Ultravox WebSocket server.
    Unlike streaming services, Ultravox processes complete audio segments,
    so this service accumulates audio data before sending for transcription.
    """

    def __init__(
        self,
        *,
        server_url: str = "ws://localhost:8765",
        language: Language = Language.EN,
        temperature: float = 0.7,
        max_tokens: int = 100,
        question: str = "Transcribe this audio.",
        audio_format: str = "raw_pcm",
        max_audio_duration_s: float = 300.0,
        persistent_connection: bool = True,
        **kwargs,
    ):
        """Initialize the Ultravox STT service.

        Args:
            server_url: Ultravox WebSocket server URL.
            language: Language for speech recognition.
            temperature: Sampling temperature for generation.
            max_tokens: Maximum tokens for transcription output.
            question: Question/instruction for the model.
            audio_format: Audio format hint (Note: pipeline audio is always sent as raw_pcm).
            max_audio_duration_s: Maximum audio duration in seconds.
            persistent_connection: Whether to maintain persistent WebSocket connection.
            **kwargs: Additional arguments passed to the parent STTService.
        """
        super().__init__(**kwargs)

        # Validate server URL
        parsed_url = urlparse(server_url)
        if parsed_url.scheme not in ("ws", "wss"):
            raise ValueError(f"Invalid WebSocket URL scheme: {parsed_url.scheme}")

        self._server_url = server_url
        self._language = language
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._question = question
        self._audio_format = audio_format
        self._max_audio_duration_s = max_audio_duration_s
        self._persistent_connection = persistent_connection

        # Connection state
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connection_lock = asyncio.Lock()
        
        # Audio accumulation state
        self._audio_buffer = bytearray()
        self._is_speaking = False
        self._processing_audio = False  # Prevent overlapping requests
        
        # Request tracking
        self._active_requests: Dict[str, asyncio.Event] = {}
        
        # Set model name for metrics
        self.set_model_name("ultravox")

    @property
    def vad_enabled(self) -> bool:
        """VAD is handled by the pipeline, not Ultravox server."""
        return False

    def can_generate_metrics(self) -> bool:
        """Check if this service can generate processing metrics."""
        return True

    async def set_model(self, model: str):
        """Set the model (not directly supported by Ultravox server)."""
        await super().set_model(model)
        logger.info(f"Model setting not supported by Ultravox server: {model}")

    async def set_language(self, language: Language):
        """Set the recognition language."""
        logger.info(f"Switching STT language to: [{language}]")
        self._language = language

    async def set_question(self, question: str):
        """Set the question/instruction for the model."""
        logger.info(f"Setting transcription question: {question}")
        self._question = question

    async def start(self, frame: StartFrame):
        """Start the Ultravox STT service."""
        await super().start(frame)
        logger.debug(f"Starting Ultravox STT service with server: {self._server_url}")
        
        if self._persistent_connection:
            await self._connect()

    async def stop(self, frame: EndFrame):
        """Stop the Ultravox STT service."""
        await super().stop(frame)
        await self._finalize_audio()
        await self._disconnect()

    async def cancel(self, frame: CancelFrame):
        """Cancel the Ultravox STT service."""
        await super().cancel(frame)
        await self._cancel_active_requests()
        await self._disconnect()

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Accumulate audio data for batch transcription."""
        # Don't accumulate if already processing or not speaking
        if self._processing_audio or not self._is_speaking:
            yield None
            return
            
        # Add audio to buffer
        self._audio_buffer.extend(audio)
        
        # Check if audio buffer is getting too long (safety limit)
        max_buffer_size = int(self._max_audio_duration_s * self.sample_rate * 2)  # 16-bit audio
        if len(self._audio_buffer) > max_buffer_size:
            logger.warning(f"Audio buffer exceeded maximum size ({len(self._audio_buffer)} > {max_buffer_size}), triggering transcription")
            await self._transcribe_accumulated_audio()
        
        yield None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process frames with Ultravox-specific handling."""
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStartedSpeakingFrame):
            logger.debug("User started speaking - beginning audio accumulation")
            self._is_speaking = True
            await self.start_ttfb_metrics()
            await self.start_processing_metrics()
            
        elif isinstance(frame, UserStoppedSpeakingFrame):
            logger.debug("User stopped speaking - triggering transcription")
            self._is_speaking = False
            # Immediately trigger transcription when speech stops
            if self._audio_buffer and not self._processing_audio:
                await self._transcribe_accumulated_audio()
            else:
                logger.debug("Skipping transcription: no audio buffer or already processing")

    async def _connect(self):
        """Establish WebSocket connection to Ultravox server."""
        if self._websocket and not self._websocket.closed:
            return

        async with self._connection_lock:
            if self._websocket and not self._websocket.closed:
                return
                
            try:
                logger.debug(f"Connecting to Ultravox server: {self._server_url}")
                self._websocket = await websockets.connect(
                    self._server_url,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=None
                )
                logger.info("Connected to Ultravox server")
                
                # Start message handler
                if self._persistent_connection:
                    asyncio.create_task(self._message_handler())
                    
            except Exception as e:
                logger.error(f"Failed to connect to Ultravox server: {e}")
                self._websocket = None
                raise

    async def _disconnect(self):
        """Close WebSocket connection."""
        async with self._connection_lock:
            if self._websocket and not self._websocket.closed:
                logger.debug("Disconnecting from Ultravox server")
                try:
                    await self._websocket.close()
                except Exception as e:
                    logger.warning(f"Error closing WebSocket: {e}")
                finally:
                    self._websocket = None

    async def _transcribe_accumulated_audio(self):
        """Send accumulated audio for transcription."""
        if not self._audio_buffer or self._processing_audio:
            logger.debug(f"Skipping transcription: buffer_empty={not self._audio_buffer}, processing={self._processing_audio}")
            return

        try:
            # Mark as processing to prevent overlapping requests
            self._processing_audio = True
            
            # Prepare audio data
            audio_bytes = bytes(self._audio_buffer)
            audio_size = len(audio_bytes)
            self._audio_buffer.clear()
            
            logger.debug(f"Processing {audio_size} audio bytes for transcription")
            
            # Skip if audio is too small (likely silence or noise)
            min_audio_size = int(self.sample_rate * 0.5 * 2)  # 0.5 seconds of 16-bit audio
            if audio_size < min_audio_size:
                logger.debug(f"Skipping transcription: audio too small ({audio_size} < {min_audio_size} bytes)")
                return
            
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Generate request ID
            request_id = f"ultravox-{uuid.uuid4()}"
            
            # Audio from piopiy pipeline is raw PCM, so use "raw_pcm" format
            # regardless of the configured audio_format
            audio_format = "raw_pcm"
            
            # Prepare language-specific question
            question = self._question
            if self._language != Language.EN:
                question = f"Please transcribe this audio in {self._language.value}. {self._question}"
            
            # Prepare request
            request = {
                "type": "transcribe",
                "audio_data": audio_b64,
                "audio_format": audio_format,
                "language": self._language.value,
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                "question": question,
                "request_id": request_id
            }
            
            # Track active request
            self._active_requests[request_id] = asyncio.Event()
            
            # Connect if needed (for non-persistent mode)
            if not self._persistent_connection or not self._websocket or self._websocket.closed:
                await self._connect()
            
            # Send request
            logger.debug(f"Sending transcription request: {request_id} ({audio_size} bytes)")
            await self._websocket.send(json.dumps(request))
            
            # For non-persistent connections, handle response directly
            if not self._persistent_connection:
                await self._handle_single_response()
                await self._disconnect()
            else:
                # For persistent connections, wait for the response (with timeout)
                try:
                    await asyncio.wait_for(self._active_requests[request_id].wait(), timeout=60.0)
                    logger.debug(f"Request {request_id} completed successfully")
                except asyncio.TimeoutError:
                    logger.warning(f"Transcription request {request_id} timed out")
                    if request_id in self._active_requests:
                        del self._active_requests[request_id]
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            await self.push_error(ErrorFrame(f"Transcription error: {e}"))
            await self.stop_all_metrics()
        finally:
            # Always reset processing state
            logger.debug("Resetting processing state")
            self._processing_audio = False

    async def _handle_single_response(self):
        """Handle response for non-persistent connection."""
        try:
            while True:
                message = await self._websocket.recv()
                data = json.loads(message)
                await self._process_message(data)
                
                # Break on completion or error
                if data.get("type") in ("completed", "error", "cancelled"):
                    break
                    
        except (ConnectionClosed, ConnectionClosedError, ConnectionClosedOK):
            logger.debug("WebSocket connection closed during response handling")
        except Exception as e:
            logger.error(f"Error handling response: {e}")
            await self.push_error(ErrorFrame(f"Response handling error: {e}"))

    async def _message_handler(self):
        """Handle incoming WebSocket messages for persistent connections."""
        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except (ConnectionClosed, ConnectionClosedError, ConnectionClosedOK):
            logger.debug("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            await self.push_error(ErrorFrame(f"Connection error: {e}"))

    @traced_stt
    async def _handle_transcription(
        self, transcript: str, is_final: bool, language: Optional[Language] = None
    ):
        """Handle a transcription result with tracing."""
        pass

    async def _process_message(self, data: Dict[str, Any]):
        """Process a message from the Ultravox server."""
        msg_type = data.get("type")
        request_id = data.get("request_id")
        
        logger.debug(f"Processing message: {msg_type} for request {request_id}")
        
        if msg_type == "started":
            logger.debug(f"Transcription started: {request_id}")
            
        elif msg_type == "completed":
            transcript = data.get("text", "").strip()
            language = Language(data.get("language", "en"))
            
            logger.info(f"Transcription completed: '{transcript}' for request {request_id}")
            
            if transcript:
                await self.stop_ttfb_metrics()
                
                # Push transcription frame
                await self.push_frame(
                    TranscriptionFrame(
                        transcript,
                        self._user_id,
                        time_now_iso8601(),
                        language,
                        result=data,
                    )
                )
                
                await self._handle_transcription(transcript, True, language)
                await self.stop_processing_metrics()
            else:
                logger.warning(f"Empty transcription received for request {request_id}")
                
            # Mark request as completed
            if request_id in self._active_requests:
                self._active_requests[request_id].set()
                del self._active_requests[request_id]
                
        elif msg_type == "error":
            error_msg = data.get("error", "Unknown error")
            logger.error(f"Transcription error for {request_id}: {error_msg}")
            await self.push_error(ErrorFrame(f"Ultravox error: {error_msg}"))
            await self.stop_all_metrics()
            
            # Mark request as completed
            if request_id in self._active_requests:
                self._active_requests[request_id].set()
                del self._active_requests[request_id]
                
        elif msg_type == "cancelled":
            logger.debug(f"Request cancelled: {request_id}")
            
            # Mark request as completed
            if request_id in self._active_requests:
                self._active_requests[request_id].set()
                del self._active_requests[request_id]
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    async def _finalize_audio(self):
        """Finalize any remaining audio in buffer."""
        # Transcribe any remaining audio (only if not already processing)
        if self._audio_buffer and not self._processing_audio:
            logger.debug("Finalizing remaining audio buffer")
            await self._transcribe_accumulated_audio()

    async def _cancel_active_requests(self):
        """Cancel all active transcription requests."""
        if not self._active_requests:
            return
            
        # Send cancel messages for active requests
        for request_id in list(self._active_requests.keys()):
            try:
                if self._websocket and not self._websocket.closed:
                    cancel_msg = {
                        "type": "cancel",
                        "request_id": request_id
                    }
                    await self._websocket.send(json.dumps(cancel_msg))
            except Exception as e:
                logger.warning(f"Error cancelling request {request_id}: {e}")

        # Wait for cancellations to complete
        for event in self._active_requests.values():
            try:
                await asyncio.wait_for(event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

        self._active_requests.clear()
