# import asyncio
# import json
# import websockets
# from typing import AsyncGenerator, Optional, Dict, Any
# from loguru import logger
# import time


# from piopiy.frames.frames import (
#     BotStoppedSpeakingFrame,
#     CancelFrame,
#     EndFrame,
#     ErrorFrame,
#     Frame,
#     LLMFullResponseEndFrame,
#     StartFrame,
#     StartInterruptionFrame,
#     TTSAudioRawFrame,
#     TTSSpeakFrame,
#     TTSStartedFrame,
#     TTSStoppedFrame,
# )


# from piopiy.processors.frame_processor import FrameDirection
# from piopiy.services.ai_services import AudioContextWordTTSService, TTSService
# from piopiy.services.websocket_service import WebsocketService
# from piopiy.transcriptions.language import Language
# from piopiy.utils.tracing.service_decorators import traced_tts


# class ChatterboxWebSocketService(TTSService):
#     """WebSocket-based Chatterbox TTS service for piopyi pipelines"""

#     def __init__(
#         self,
#         websocket_url: str = "ws://103.247.19.245:60027",
#         # voice_prompt_path: Optional[str] = None,
#         streaming_mode: bool = True,
#         sample_rate: int = 24000,
#         # Chatterbox-specific parameters
#         chunk_size: int = 75,
#         exaggeration: float = 0.5,
#         temperature: float = 0.8,
#         cfg_weight: float = 0.5,
#         context_window: int = 70,
#         fade_duration: float = 0.09,
#         # Interruption handling
#         reconnect_on_interrupt: bool = False,  # Whether to reconnect on interruption
#         **kwargs
#     ):
#         # Initialize with required sample rate
#         super().__init__(sample_rate=sample_rate, **kwargs)
        
#         self._websocket_url = websocket_url
#         # self._voice_prompt_path = voice_prompt_path
#         self._streaming_mode = streaming_mode
#         self._sample_rate = sample_rate
        
#         # Chatterbox parameters
#         self._chunk_size = chunk_size
#         self._exaggeration = exaggeration
#         self._temperature = temperature
#         self._cfg_weight = cfg_weight
#         self._context_window = context_window
#         self._fade_duration = fade_duration
        
#         # Interruption handling
#         self._reconnect_on_interrupt = reconnect_on_interrupt
        
#         self._websocket: Optional[websockets.WebSocketClientProtocol] = None
#         self._session_id: Optional[str] = None
#         self._is_generating = False
#         self._connection_lock = asyncio.Lock()
#         self._started = False
#         self._connect_timeout = 10.0
#         self._max_retries = 3
#         self._current_request_id = 0
#         self._current_session_id = None  # Track current session for interruption
#         self._pending_stream_ready = None  # ADD THIS LINE
        
#         logger.info(f"Chatterbox WebSocket service initialized for {websocket_url}")

#     async def start(self, frame: Frame) -> None:
#         """Start the service and establish WebSocket connection"""
#         await super().start(frame)
#         self._started = True
        
#         # Try to establish connection with retries
#         for attempt in range(self._max_retries):
#             try:
#                 await self._ensure_connection()
#                 break
#             except Exception as e:
#                 logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
#                 if attempt == self._max_retries - 1:
#                     logger.error("Failed to establish WebSocket connection after all retries")
#                     raise
#                 # await asyncio.sleep(0.09)

#     async def stop(self, frame: Frame) -> None:
#         """Stop the service and close WebSocket connection"""
#         self._started = False
#         await self._close_connection()
#         await super().stop(frame)

#     async def cancel(self, frame: CancelFrame) -> None:
#         """Cancel any ongoing generation"""
#         if self._is_generating:
#             # Handle cancellation similar to interruption
#             await self._stop_generation()
#         await super().cancel(frame)
    
#     async def _stop_generation(self):
#         """Stop ongoing generation cleanly"""
#         if not self._is_generating:
#             return
            
#         logger.info("Stopping ongoing TTS generation")
#         self._is_generating = False
        
#         # If in streaming mode and we have a session, send stream_end
#         if self._streaming_mode and self._current_session_id and self._websocket and self._is_connected():
#             try:
#                 await self._websocket.send(json.dumps({
#                     "type": "stream_end"
#                 }))
#                 logger.info(f"Sent stream_end for session {self._current_session_id}")
#             except Exception as e:
#                 logger.error(f"Error sending stream_end: {e}")

#     async def _ensure_connection(self):
#         """Ensure WebSocket connection is established"""
#         if not self._started:
#             return
            
#         async with self._connection_lock:
#             if self._websocket is None or not self._is_connected():
#                 await self._connect()

#     async def _connect(self):
#         """Establish WebSocket connection"""
#         try:
#             logger.info(f"Connecting to Chatterbox WebSocket server at {self._websocket_url}")
            
#             self._websocket = await asyncio.wait_for(
#                 websockets.connect(
#                     self._websocket_url,
#                     ping_interval=30,
#                     ping_timeout=10,
#                     close_timeout=5,
#                     max_size=16 * 1024 * 1024  # 16MB max message size
#                 ),
#                 timeout=self._connect_timeout
#             )
            
#             logger.info("Chatterbox WebSocket connected successfully")
            
#             # Test the connection by sending a ping or waiting for any initial message
#             # try:
#             #     # Some servers send an initial message on connection
#             #     test_msg = await asyncio.wait_for(self._websocket.recv(), timeout=0.05)
#             #     logger.info(f"Received initial message from server: {test_msg}")
#             # except asyncio.TimeoutError:
#             #     # No initial message, that's fine
#             #     logger.debug("No initial message from server (this is normal)")
            
#         except Exception as e:
#             logger.error(f"Failed to connect to Chatterbox WebSocket server: {e}")
#             if self._websocket:
#                 try:
#                     await self._websocket.close()
#                 except:
#                     pass
#             self._websocket = None
#             raise

#     async def _close_connection(self):
#         """Close WebSocket connection"""
#         async with self._connection_lock:
#             if self._websocket:
#                 try:
#                     await self._websocket.close()
#                 except Exception as e:
#                     logger.error(f"Error closing WebSocket connection: {e}")
#                 finally:
#                     self._websocket = None
#                     self._session_id = None
#                     logger.info("Chatterbox WebSocket connection closed")

#     def _is_connected(self) -> bool:
#         """Check if WebSocket is connected - handles different websocket library versions"""
#         if not self._websocket:
#             return False
            
#         # Try different attributes that might indicate connection state
#         if hasattr(self._websocket, 'closed'):
#             return not self._websocket.closed
#         elif hasattr(self._websocket, 'open'):
#             return self._websocket.open
#         elif hasattr(self._websocket, 'state'):
#             # Some libraries use state attribute with specific values
#             try:
#                 import websockets
#                 if hasattr(websockets, 'protocol') and hasattr(websockets.protocol, 'State'):
#                     return self._websocket.state == websockets.protocol.State.OPEN
#             except:
#                 pass
#             # Fallback: check numeric state (1 usually means OPEN)
#             state = getattr(self._websocket, 'state', None)
#             return state == 1 if state is not None else True
#         else:
#             # If we can't determine state, assume connected if websocket exists
#             # This is safer than crashing
#             return True

#     @traced_tts
#     async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
#         """Generate TTS audio from text via WebSocket"""
#         if not self._started:
#             yield ErrorFrame("Chatterbox service not started")
#             return
            
#         try:
                        
#             await self._ensure_connection()
            
#             if not self._websocket or not self._is_connected():
#                 # Try to reconnect once
#                 try:
#                     await self._connect()
#                 except Exception as e:
#                     yield ErrorFrame(f"Chatterbox WebSocket connection failed: {str(e)}")
#                     return

#             logger.info(f"TTS for text: '{text[:60]}{'...' if len(text) > 50 else ''}'")
            
#             # Send TTS started frame
#             yield TTSStartedFrame()
            
#             self._is_generating = True
            
#             try:
#                 if self._streaming_mode:
#                     # Use streaming mode
#                     async for frame in self._stream_synthesis(text):
#                         yield frame
#                 else:
#                     # Use non-streaming mode
#                     async for frame in self._synthesize(text):
#                         yield frame
                        
#             except Exception as e:
#                 # if isinstance(frame, ErrorFrame):
#                 #     logger.error(f"TTS error: {frame.error!r}")  # Shows None, '', or message

#                 logger.error(f"Error during TTS generation: {e!r}", exc_info=True)
#                 yield ErrorFrame(f"TTS generation failed: {str(e)}")
                
#         except Exception as e:
#             logger.error(f"Error in TTS generation: {e}")
#             yield ErrorFrame(f"TTS generation failed: {str(e)}")
#         finally:
#             self._is_generating = False
#             yield TTSStoppedFrame()



#     async def _synthesize(self, text: str) -> AsyncGenerator[Frame, None]:
#         """Non-streaming synthesis mode"""
#         self._current_request_id += 1
#         request_id = f"req_{self._current_request_id}"
        
#         # Prepare synthesis request
#         request = {
#             "type": "synthesize",
#             "text": text,
#             "request_id": request_id,
#             "params": {
#                 "chunk_size": self._chunk_size,
#                 "exaggeration": self._exaggeration,
#                 "temperature": self._temperature,
#                 "cfg_weight": self._cfg_weight,
#                 "context_window": self._context_window,
#                 "fade_duration": self._fade_duration
#             }
#         }
        
#         # if self._voice_prompt_path:
#         #     request["params"]["voice_prompt_path"] = self._voice_prompt_path
            
#         # Send request
#         await self._websocket.send(json.dumps(request))
        
#         # Receive response
#         while self._is_generating:
#             try:
#                 message = await asyncio.wait_for(self._websocket.recv(), timeout=30.0)
                
#                 # Parse JSON response
#                 data = json.loads(message)
                
#                 if data["type"] == "audio":
#                     # Decode base64 audio
#                     import base64
#                     audio_bytes = base64.b64decode(data["audio_content"])
                    
#                     yield TTSAudioRawFrame(
#                         audio=audio_bytes,
#                         sample_rate=data.get("sample_rate", self._sample_rate),
#                         num_channels=data.get("channels", 1)
#                     )
                    
#                 elif data["type"] == "synthesis_complete":
#                     logger.info(f"Synthesis completed for request {request_id}")
#                     break
                    
#                 elif data["type"] == "error":
#                     logger.error(f"Synthesis error: {data.get('error')}")
#                     yield ErrorFrame(f"Synthesis error: {data.get('error')}")
#                     break
                    
#             except asyncio.TimeoutError:
#                 logger.error("Timeout waiting for synthesis response")
#                 yield ErrorFrame("Synthesis timeout")
#                 break
#             except Exception as e:
#                 logger.error(f"Error receiving synthesis response: {e}")
#                 yield ErrorFrame(f"Synthesis error: {str(e)}")
#                 break

#     async def _drain_pending_messages(self, timeout: float = 0.01):
#         """Drain any pending messages from the WebSocket to avoid race conditions"""
#         drained_count = 0
#         current_time = time.time()
#         try:
#             while True:
#                 try:
#                     msg = await asyncio.wait_for(self._websocket.recv(), timeout=timeout)
#                     drained_count += 1
#                     if isinstance(msg, str):
#                         data = json.loads(msg)
#                         msg_session = data.get("session_id")
#                         msg_type = data.get("type", "unknown")
#                         if msg_type == "stream_ready" and msg_session == self._current_session_id:
#                         # This is actually what we're waiting for!
#                             self._pending_stream_ready = data
#                             break
#                         logger.debug(f"Drained pending message: {data.get('type', 'unknown')}")
#                     else:
#                         logger.debug(f"Drained pending binary message: {len(msg)} bytes")
#                 except asyncio.TimeoutError:
#                     break
#         except Exception as e:
#             logger.warning(f"Error draining messages: {e}")
        
#         if drained_count > 0:
#             logger.info(f"Drained {drained_count} pending messages")
    

#     async def _stream_synthesis(self, text: str) -> AsyncGenerator[Frame, None]:
#         session_id = f"session_{self._current_request_id}"
#         self._current_request_id += 1
#         self._current_session_id = session_id

#         logger.info(f"=== Starting streaming synthesis for session {session_id} ===")

#         self._pending_stream_ready = None
#         await self._drain_pending_messages()
#         await asyncio.sleep(0.05)

#         # Send stream_start
#         stream_start = {
#             "type": "stream_start",
#             "session_id": session_id,
#             "params": {
#                 # "voice_prompt_path": self._voice_prompt_path,
#                 "chunk_size": self._chunk_size,
#                 "exaggeration": self._exaggeration,
#                 "temperature": self._temperature,
#                 "cfg_weight": self._cfg_weight,
#                 "context_window": self._context_window,
#                 "fade_duration": self._fade_duration
#             }
#         }



#         logger.info(f"Sending stream_start message")
#         await self._websocket.send(json.dumps(stream_start))
#         logger.info(f"stream_start message sent successfully")



#         if self._pending_stream_ready and self._pending_stream_ready.get("session_id")==session_id :
#             logger.info(f"Using stream_ready found during draining for session {session_id}")
#         else:

#             # Wait for stream_ready
#             logger.info("Waiting for stream_ready response...")
#             max_wait = 20
#             deadline = asyncio.get_event_loop().time() + max_wait
#             while True:
#                 left = deadline - asyncio.get_event_loop().time()
#                 if left <= 0:
#                     # logger.error("Timeout waiting for stream_ready")
#                     yield ErrorFrame("Stream initialization timeout")
#                     return
#                 try:
#                     msg = await asyncio.wait_for(self._websocket.recv(), timeout=min(20, left))
#                 except asyncio.TimeoutError:
#                     logger.error("Timeout waiting for stream_ready (server slow or down)")
#                     yield ErrorFrame("Stream initialization timeout. Please try again later.")
#                     return
                

#                 if isinstance(msg, str):
#                     try:
#                         data = json.loads(msg)
#                     except Exception:
#                         logger.warning("Malformed JSON while waiting for stream_ready")
#                         continue
#                     # Ignore any message NOT for this session
#                     if data.get("session_id") and data.get("session_id") != session_id:
#                         logger.warning(f"Ignoring message for old session: {data}")   #-------> comment it
#                         continue
#                     if data.get("type") == "stream_ready" and data.get("session_id") == session_id:
#                         logger.info(f"Stream ready for session {session_id}")
#                         break
#                     elif data.get("type") == "error":
#                         logger.error(f"Server error: {data.get('error')}")
#                         yield ErrorFrame(f"Server error: {data.get('error', 'Unknown error')}")
#                         return
#                     else:
#                         logger.warning(f"Unexpected message while waiting for stream_ready: {data}")
#                         continue
#                 else:
#                     # It's probably a binary audio chunk for a previous session, just ignore and log
#                     logger.warning("Ignoring unexpected binary message while waiting for stream_ready")
#                     continue
#         self._pending_stream_ready = None


#         logger.info(f"[TIMING] Client about to send text and flush at {time.time()}")

#         # Send both messages concurrently
#         await asyncio.gather(
#             self._websocket.send(json.dumps({
#                 "type": "stream_text",
#                 "text": text
#             })),
#             self._websocket.send(json.dumps({
#                 "type": "stream_flush"
#             }))
#         )

#         logger.info(f"[TIMING] Client sent both messages at {time.time()}")

#         chunk_count = 0
#         stream_completed = False
#         first_audio_time = None

#         try:
#             while self._is_generating:
#                 try:
#                     message = await asyncio.wait_for(self._websocket.recv(), timeout=0.1)

#                     if first_audio_time is None:
#                         first_audio_time = time.time()
#                         logger.info(f"[TIMING] Client received first audio message at {first_audio_time}")
#                     if isinstance(message, str):
#                         data = json.loads(message)
#                         if data["type"] == "audio_chunk":
#                             # chunk_index = data.get("chunk_index", chunk_count)

#                             audio_data = await asyncio.wait_for(self._websocket.recv(), timeout=0.05)

#                             if isinstance(audio_data, bytes):
#                                 yield TTSAudioRawFrame(
#                                     audio=audio_data,
#                                     sample_rate=data.get("sample_rate", self._sample_rate),
#                                     num_channels=data.get("channels", 1)
#                                 )
#                                 chunk_count += 1

#                         elif data["type"] == "stream_complete":
#                             logger.info(f"Stream completed for session {session_id}, {chunk_count} chunks")
#                             stream_completed = True
#                             break
#                         elif data["type"] == "error":
#                             logger.error(f"Stream error: {data.get('error')}")
#                             yield ErrorFrame(f"Stream error: {data.get('error')}")
#                             break
#                     elif isinstance(message, bytes):
#                         yield TTSAudioRawFrame(
#                             audio=message,
#                             sample_rate=self._sample_rate,
#                             num_channels=1
#                         )
#                         chunk_count += 1
#                 except asyncio.TimeoutError:
#                     if not self._is_generating:
#                         logger.info("Generation stopped by interruption, sending stream_end")
#                         break
#                     continue
#                 except websockets.exceptions.ConnectionClosed:
#                     logger.warning("WebSocket connection closed during streaming")
#                     break
#                 except websockets.exceptions.ConnectionClosedOK:
#                     logger.info("WebSocket connection closed normally")
#                     break
#                 except Exception as e:
#                     logger.error(f"Error receiving stream data: {e}", exc_info=True)
#                     yield ErrorFrame(f"Stream error: {str(e)}")
#                     break
#         finally:
#             # not stream_completed and self._websocket and self._is_connected() and 
#             if self._current_session_id == session_id:
#                 if not stream_completed and self._websocket and self._is_connected():
#                     try:
#                         # logger.info(f"Sending stream_end for incomplete session {session_id}")
#                         await self._websocket.send(json.dumps({
#                             "type": "stream_end"
#                         }))
#                         # await asyncio.sleep(0.2)    #--------> Add a longer delay after stopping a session before starting a new one:
#                         await self._drain_pending_messages(timeout=0.2)

#                     except Exception as e:
#                         # logger.error(f"Error sending stream_end: {e}")
#                         logger.error(f"Error in cleanup: {e}")
#             self._current_request_id = None
#             self._pending_stream_ready = None

            
#             # if self._current_session_id == session_id:
#             #     self._current_session_id = None
#             # logger.info(f"=== Completed streaming synthesis for session {session_id} ===")


#     async def _handle_interruption(self, frame: StartInterruptionFrame, direction: FrameDirection):
#         """Handle interruption when user speaks while TTS is playing"""
#         logger.info("Received StartInterruptionFrame! User started speaking.")
#         await super()._handle_interruption(frame, direction)
        
#         # Since Chatterbox doesn't have explicit interrupt messages like StyleTTS2,
#         # we need to handle this differently
#         if self._is_generating and self._websocket and self._is_connected():
#             logger.info("User interrupted - stopping Chatterbox generation")
            
#             # Set flag to stop receiving audio
#             self._is_generating = False
            
#             # If in streaming mode, send stream_end to cleanly stop
#             if self._streaming_mode and self._session_id:
#                 try:
#                     await self._websocket.send(json.dumps({
#                         "type": "stream_end"
#                     }))
#                     logger.info("Sent stream_end to stop generation")
#                     # Drain any pending messages to clear the buffer    
#                     await self._drain_pending_messages(timeout=0.5)
#                 except Exception as e:
#                     logger.error(f"Error sending stream_end: {e}")
            
#             # Option 1: Close and reconnect for clean state (if enabled)
#             if self._reconnect_on_interrupt:
#                 try:
#                     await self._close_connection()
#                     # await asyncio.sleep(0.1)  # Brief pause
#                     await self._ensure_connection()
#                     logger.info("Reconnected after interruption")
#                 except Exception as e:
#                     logger.error(f"Error during interruption reconnect: {e}")
#             else:
#                 # Option 2: Just stop processing without reconnecting
#                 # Clear any session state
#                 self._current_session_id = None
#                 self._pending_stream_ready = None
import asyncio
import json
import websockets
from typing import AsyncGenerator, Optional, Dict, Any
from loguru import logger
import time


from pipecat.frames.frames import (
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


from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.ai_services import AudioContextWordTTSService, TTSService
from pipecat.services.websocket_service import WebsocketService
from pipecat.transcriptions.language import Language
from pipecat.utils.tracing.service_decorators import traced_tts


class ChatterboxWebSocketService(TTSService):
    """WebSocket-based Chatterbox TTS service for pipecat pipelines"""

    def __init__(
        self,
        websocket_url: str = "ws://103.247.19.245:60027",
        # voice_prompt_path: Optional[str] = None,
        streaming_mode: bool = True,
        sample_rate: int = 24000,
        # Chatterbox-specific parameters
        chunk_size: int = 75,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        context_window: int = 70,
        fade_duration: float = 0.09,
        # Interruption handling
        reconnect_on_interrupt: bool = False,  # Whether to reconnect on interruption
        **kwargs
    ):
        # Initialize with required sample rate
        super().__init__(sample_rate=sample_rate, **kwargs)
        
        self._websocket_url = websocket_url
        # self._voice_prompt_path = voice_prompt_path
        self._streaming_mode = streaming_mode
        self._sample_rate = sample_rate
        
        # Chatterbox parameters
        self._chunk_size = chunk_size
        self._exaggeration = exaggeration
        self._temperature = temperature
        self._cfg_weight = cfg_weight
        self._context_window = context_window
        self._fade_duration = fade_duration
        
        # Interruption handling
        self._reconnect_on_interrupt = reconnect_on_interrupt
        
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._session_id: Optional[str] = None
        self._is_generating = False
        self._connection_lock = asyncio.Lock()
        self._started = False
        self._connect_timeout = 10.0
        self._max_retries = 3
        self._current_request_id = 0
        self._current_session_id = None  # Track current session for interruption
        self._pending_stream_ready = None  # ADD THIS LINE
        
        logger.info(f"Chatterbox WebSocket service initialized for {websocket_url}")

    async def start(self, frame: Frame) -> None:
        """Start the service and establish WebSocket connection"""
        await super().start(frame)
        self._started = True
        
        # Try to establish connection with retries
        for attempt in range(self._max_retries):
            try:
                await self._ensure_connection()
                break
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == self._max_retries - 1:
                    logger.error("Failed to establish WebSocket connection after all retries")
                    raise
                # await asyncio.sleep(0.09)

    async def stop(self, frame: Frame) -> None:
        """Stop the service and close WebSocket connection"""
        self._started = False
        await self._close_connection()
        await super().stop(frame)

    async def cancel(self, frame: CancelFrame) -> None:
        """Cancel any ongoing generation"""
        if self._is_generating:
            # Handle cancellation similar to interruption
            await self._stop_generation()
        await super().cancel(frame)
    
    async def _stop_generation(self):
        """Stop ongoing generation cleanly"""
        if not self._is_generating:
            return
            
        logger.info("Stopping ongoing TTS generation")
        self._is_generating = False
        
        # If in streaming mode and we have a session, send stream_end
        if self._streaming_mode and self._current_session_id and self._websocket and self._is_connected():
            try:
                await self._websocket.send(json.dumps({
                    "type": "stream_end"
                }))
                logger.info(f"Sent stream_end for session {self._current_session_id}")
            except Exception as e:
                logger.error(f"Error sending stream_end: {e}")

    async def _ensure_connection(self):
        """Ensure WebSocket connection is established"""
        if not self._started:
            return
            
        async with self._connection_lock:
            if self._websocket is None or not self._is_connected():
                await self._connect()

    async def _connect(self):
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to Chatterbox WebSocket server at {self._websocket_url}")
            
            self._websocket = await asyncio.wait_for(
                websockets.connect(
                    self._websocket_url,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5,
                    max_size=16 * 1024 * 1024  # 16MB max message size
                ),
                timeout=self._connect_timeout
            )
            
            logger.info("Chatterbox WebSocket connected successfully")
            
            # Test the connection by sending a ping or waiting for any initial message
            # try:
            #     # Some servers send an initial message on connection
            #     test_msg = await asyncio.wait_for(self._websocket.recv(), timeout=0.05)
            #     logger.info(f"Received initial message from server: {test_msg}")
            # except asyncio.TimeoutError:
            #     # No initial message, that's fine
            #     logger.debug("No initial message from server (this is normal)")
            
        except Exception as e:
            logger.error(f"Failed to connect to Chatterbox WebSocket server: {e}")
            if self._websocket:
                try:
                    await self._websocket.close()
                except:
                    pass
            self._websocket = None
            raise

    async def _close_connection(self):
        """Close WebSocket connection"""
        async with self._connection_lock:
            if self._websocket:
                try:
                    await self._websocket.close()
                except Exception as e:
                    logger.error(f"Error closing WebSocket connection: {e}")
                finally:
                    self._websocket = None
                    self._session_id = None
                    logger.info("Chatterbox WebSocket connection closed")

    def _is_connected(self) -> bool:
        """Check if WebSocket is connected - handles different websocket library versions"""
        if not self._websocket:
            return False
            
        # Try different attributes that might indicate connection state
        if hasattr(self._websocket, 'closed'):
            return not self._websocket.closed
        elif hasattr(self._websocket, 'open'):
            return self._websocket.open
        elif hasattr(self._websocket, 'state'):
            # Some libraries use state attribute with specific values
            try:
                import websockets
                if hasattr(websockets, 'protocol') and hasattr(websockets.protocol, 'State'):
                    return self._websocket.state == websockets.protocol.State.OPEN
            except:
                pass
            # Fallback: check numeric state (1 usually means OPEN)
            state = getattr(self._websocket, 'state', None)
            return state == 1 if state is not None else True
        else:
            # If we can't determine state, assume connected if websocket exists
            # This is safer than crashing
            return True

    @traced_tts
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Generate TTS audio from text via WebSocket"""
        if not self._started:
            yield ErrorFrame("Chatterbox service not started")
            return
            
        try:
                        
            await self._ensure_connection()
            
            if not self._websocket or not self._is_connected():
                # Try to reconnect once
                try:
                    await self._connect()
                except Exception as e:
                    yield ErrorFrame(f"Chatterbox WebSocket connection failed: {str(e)}")
                    return

            logger.info(f"TTS for text: '{text[:60]}{'...' if len(text) > 50 else ''}'")
            
            # Send TTS started frame
            yield TTSStartedFrame()
            
            self._is_generating = True
            
            try:
                if self._streaming_mode:
                    # Use streaming mode
                    async for frame in self._stream_synthesis(text):
                        yield frame
                else:
                    # Use non-streaming mode
                    async for frame in self._synthesize(text):
                        yield frame
                        
            except Exception as e:
                # if isinstance(frame, ErrorFrame):
                #     logger.error(f"TTS error: {frame.error!r}")  # Shows None, '', or message

                logger.error(f"Error during TTS generation: {e!r}", exc_info=True)
                yield ErrorFrame(f"TTS generation failed: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in TTS generation: {e}")
            yield ErrorFrame(f"TTS generation failed: {str(e)}")
        finally:
            self._is_generating = False
            yield TTSStoppedFrame()



    async def _synthesize(self, text: str) -> AsyncGenerator[Frame, None]:
        """Non-streaming synthesis mode"""
        self._current_request_id += 1
        request_id = f"req_{self._current_request_id}"
        
        # Prepare synthesis request
        request = {
            "type": "synthesize",
            "text": text,
            "request_id": request_id,
            "params": {
                "chunk_size": self._chunk_size,
                "exaggeration": self._exaggeration,
                "temperature": self._temperature,
                "cfg_weight": self._cfg_weight,
                "context_window": self._context_window,
                "fade_duration": self._fade_duration
            }
        }
        
        # if self._voice_prompt_path:
        #     request["params"]["voice_prompt_path"] = self._voice_prompt_path
            
        # Send request
        await self._websocket.send(json.dumps(request))
        
        # Receive response
        while self._is_generating:
            try:
                message = await asyncio.wait_for(self._websocket.recv(), timeout=30.0)
                
                # Parse JSON response
                data = json.loads(message)
                
                if data["type"] == "audio":
                    # Decode base64 audio
                    import base64
                    audio_bytes = base64.b64decode(data["audio_content"])
                    
                    yield TTSAudioRawFrame(
                        audio=audio_bytes,
                        sample_rate=data.get("sample_rate", self._sample_rate),
                        num_channels=data.get("channels", 1)
                    )
                    
                elif data["type"] == "synthesis_complete":
                    logger.info(f"Synthesis completed for request {request_id}")
                    break
                    
                elif data["type"] == "error":
                    logger.error(f"Synthesis error: {data.get('error')}")
                    yield ErrorFrame(f"Synthesis error: {data.get('error')}")
                    break
                    
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for synthesis response")
                yield ErrorFrame("Synthesis timeout")
                break
            except Exception as e:
                logger.error(f"Error receiving synthesis response: {e}")
                yield ErrorFrame(f"Synthesis error: {str(e)}")
                break

    async def _drain_pending_messages(self, timeout: float = 0.01):
        """Drain any pending messages from the WebSocket to avoid race conditions"""
        drained_count = 0
        current_time = time.time()
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(self._websocket.recv(), timeout=timeout)
                    drained_count += 1
                    if isinstance(msg, str):
                        data = json.loads(msg)
                        msg_session = data.get("session_id")
                        msg_type = data.get("type", "unknown")
                        if msg_type == "stream_ready" and msg_session == self._current_session_id:
                        # This is actually what we're waiting for!
                            self._pending_stream_ready = data
                            break
                        logger.debug(f"Drained pending message: {data.get('type', 'unknown')}")
                    else:
                        logger.debug(f"Drained pending binary message: {len(msg)} bytes")
                except asyncio.TimeoutError:
                    break
        except Exception as e:
            logger.warning(f"Error draining messages: {e}")
        
        if drained_count > 0:
            logger.info(f"Drained {drained_count} pending messages")
    

    async def _stream_synthesis(self, text: str) -> AsyncGenerator[Frame, None]:
        session_id = f"session_{self._current_request_id}"
        self._current_request_id += 1
        self._current_session_id = session_id

        logger.info(f"=== Starting streaming synthesis for session {session_id} ===")

        self._pending_stream_ready = None
        await self._drain_pending_messages()
        await asyncio.sleep(0.05)

        # Send stream_start
        stream_start = {
            "type": "stream_start",
            "session_id": session_id,
            "params": {
                # "voice_prompt_path": self._voice_prompt_path,
                "chunk_size": self._chunk_size,
                "exaggeration": self._exaggeration,
                "temperature": self._temperature,
                "cfg_weight": self._cfg_weight,
                "context_window": self._context_window,
                "fade_duration": self._fade_duration
            }
        }



        logger.info(f"Sending stream_start message")
        await self._websocket.send(json.dumps(stream_start))
        logger.info(f"stream_start message sent successfully")



        if self._pending_stream_ready and self._pending_stream_ready.get("session_id")==session_id :
            logger.info(f"Using stream_ready found during draining for session {session_id}")
        else:

            # Wait for stream_ready
            logger.info("Waiting for stream_ready response...")
            max_wait = 20
            deadline = asyncio.get_event_loop().time() + max_wait
            while True:
                left = deadline - asyncio.get_event_loop().time()
                if left <= 0:
                    # logger.error("Timeout waiting for stream_ready")
                    yield ErrorFrame("Stream initialization timeout")
                    return
                try:
                    msg = await asyncio.wait_for(self._websocket.recv(), timeout=min(20, left))
                except asyncio.TimeoutError:
                    logger.error("Timeout waiting for stream_ready (server slow or down)")
                    yield ErrorFrame("Stream initialization timeout. Please try again later.")
                    return
                

                if isinstance(msg, str):
                    try:
                        data = json.loads(msg)
                    except Exception:
                        logger.warning("Malformed JSON while waiting for stream_ready")
                        continue
                    # Ignore any message NOT for this session
                    if data.get("session_id") and data.get("session_id") != session_id:
                        logger.warning(f"Ignoring message for old session: {data}")   #-------> comment it
                        continue
                    if data.get("type") == "stream_ready" and data.get("session_id") == session_id:
                        logger.info(f"Stream ready for session {session_id}")
                        break
                    elif data.get("type") == "error":
                        logger.error(f"Server error: {data.get('error')}")
                        yield ErrorFrame(f"Server error: {data.get('error', 'Unknown error')}")
                        return
                    else:
                        logger.warning(f"Unexpected message while waiting for stream_ready: {data}")
                        continue
                else:
                    # It's probably a binary audio chunk for a previous session, just ignore and log
                    logger.warning("Ignoring unexpected binary message while waiting for stream_ready")
                    continue
        self._pending_stream_ready = None


        logger.info(f"[TIMING] Client about to send text and flush at {time.time()}")

        # Send both messages concurrently
        await asyncio.gather(
            self._websocket.send(json.dumps({
                "type": "stream_text",
                "text": text
            })),
            self._websocket.send(json.dumps({
                "type": "stream_flush"
            }))
        )

        logger.info(f"[TIMING] Client sent both messages at {time.time()}")

        chunk_count = 0
        stream_completed = False
        first_audio_time = None

        try:
            while self._is_generating:
                try:
                    message = await asyncio.wait_for(self._websocket.recv(), timeout=0.1)

                    if first_audio_time is None:
                        first_audio_time = time.time()
                        logger.info(f"[TIMING] Client received first audio message at {first_audio_time}")
                    if isinstance(message, str):
                        data = json.loads(message)
                        if data["type"] == "audio_chunk":
                            # chunk_index = data.get("chunk_index", chunk_count)

                            audio_data = await asyncio.wait_for(self._websocket.recv(), timeout=0.05)

                            if isinstance(audio_data, bytes):
                                yield TTSAudioRawFrame(
                                    audio=audio_data,
                                    sample_rate=data.get("sample_rate", self._sample_rate),
                                    num_channels=data.get("channels", 1)
                                )
                                chunk_count += 1

                        elif data["type"] == "stream_complete":
                            logger.info(f"Stream completed for session {session_id}, {chunk_count} chunks")
                            stream_completed = True
                            break
                        elif data["type"] == "error":
                            logger.error(f"Stream error: {data.get('error')}")
                            yield ErrorFrame(f"Stream error: {data.get('error')}")
                            break
                    elif isinstance(message, bytes):
                        yield TTSAudioRawFrame(
                            audio=message,
                            sample_rate=self._sample_rate,
                            num_channels=1
                        )
                        chunk_count += 1
                except asyncio.TimeoutError:
                    if not self._is_generating:
                        logger.info("Generation stopped by interruption, sending stream_end")
                        break
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed during streaming")
                    break
                except websockets.exceptions.ConnectionClosedOK:
                    logger.info("WebSocket connection closed normally")
                    break
                except Exception as e:
                    logger.error(f"Error receiving stream data: {e}", exc_info=True)
                    yield ErrorFrame(f"Stream error: {str(e)}")
                    break
        finally:
            if not stream_completed and self._websocket and self._is_connected() and self._current_session_id == session_id:
                try:
                    # logger.info(f"Sending stream_end for incomplete session {session_id}")
                    await self._websocket.send(json.dumps({
                        "type": "stream_end"
                    }))
                    await asyncio.sleep(0.2)    #--------> Add a longer delay after stopping a session before starting a new one:
                except Exception as e:
                    logger.error(f"Error sending stream_end: {e}")
            if self._current_session_id == session_id:
                self._current_session_id = None
            # logger.info(f"=== Completed streaming synthesis for session {session_id} ===")


    async def _handle_interruption(self, frame: StartInterruptionFrame, direction: FrameDirection):
        """Handle interruption when user speaks while TTS is playing"""
        logger.info("Received StartInterruptionFrame! User started speaking.")
        await super()._handle_interruption(frame, direction)
        
        # Since Chatterbox doesn't have explicit interrupt messages like StyleTTS2,
        # we need to handle this differently
        if self._is_generating and self._websocket and self._is_connected():
            logger.info("User interrupted - stopping Chatterbox generation")
            
            # Set flag to stop receiving audio
            self._is_generating = False
            
            # If in streaming mode, send stream_end to cleanly stop
            if self._streaming_mode and self._session_id:
                try:
                    await self._websocket.send(json.dumps({
                        "type": "stream_end"
                    }))
                    logger.info("Sent stream_end to stop generation")
                except Exception as e:
                    logger.error(f"Error sending stream_end: {e}")
            
            # Option 1: Close and reconnect for clean state (if enabled)
            if self._reconnect_on_interrupt:
                try:
                    await self._close_connection()
                    # await asyncio.sleep(0.1)  # Brief pause
                    await self._ensure_connection()
                    logger.info("Reconnected after interruption")
                except Exception as e:
                    logger.error(f"Error during interruption reconnect: {e}")
            else:
                # Option 2: Just stop processing without reconnecting
                # Clear any session state
                self._current_session_id = None