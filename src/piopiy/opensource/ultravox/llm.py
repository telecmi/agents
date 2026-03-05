# ux_client.py
"""
Piopiy client for the Ultravox WebSocket server.

Pipeline:
  Microphone → VAD → UltravoxTransport → TTS → Speaker
"""

import asyncio
import base64
import json
import uuid
import numpy as np

from loguru import logger

import websockets
from websockets.exceptions import ConnectionClosed

from piopiy.frames.frames import (
    AudioRawFrame,
    VADUserStartedSpeakingFrame,  # ADD
    VADUserStoppedSpeakingFrame,  # ADD
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    TextFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    StartFrame,
    EndFrame,
    CancelFrame,
)
from piopiy.processors.frame_processor import FrameDirection, FrameProcessor


class OpenUltravoxLLM(FrameProcessor):
    """
    Piopiy processor that:
      1. Connects to the Ultravox WS server on the first StartFrame.
      2. Buffers PCM audio while the user is speaking.
      3. Sends buffered audio when the user stops speaking.
      4. Streams partial text chunks downstream as TextFrames.
    """

    def __init__(self, server_url: str, caller_id: str, system_prompt: str = ""):
        super().__init__()
        self._server_url = server_url
        self._caller_id = caller_id
        self._system_prompt = system_prompt

        self._ws = None
        self._ws_lock = asyncio.Lock()
        self._audio_buffer: list[np.ndarray] = []
        self._collecting = False
        self._connected = False
       

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def _ensure_connected(self):
        """Connect (or reconnect) to the server if not already connected."""
        async with self._ws_lock:
            if self._connected and self._ws and not self._ws.closed:
                return True

            try:
                logger.info(f"[Ultravox] Connecting to {self._server_url} ...")
                self._ws = await websockets.connect(
                    self._server_url,
                    max_size=None,
                    open_timeout=10,
                    ping_interval=20,
                    ping_timeout=20,
                )

                connect_msg = {
                    "type": "connect",
                    "caller_id": self._caller_id,
                }
                if self._system_prompt:
                    connect_msg["system_prompt"] = self._system_prompt

                await self._ws.send(json.dumps(connect_msg))
                resp = json.loads(await self._ws.recv())

                if resp.get("type") == "connected":
                    self._connected = True
                    logger.info(f"[Ultravox] Connected — caller_id: {resp['caller_id']}")
                    return True
                else:
                    logger.error(f"[Ultravox] Unexpected connect response: {resp}")
                    self._connected = False
                    return False

            except Exception as e:
                logger.error(f"[Ultravox] Connection failed: {e}")
                self._ws = None
                self._connected = False
                return False

    async def _disconnect(self):
        async with self._ws_lock:
            self._connected = False
            if self._ws:
                try:
                    await self._ws.close()
                except Exception:
                    pass
                self._ws = None
                logger.info("[Ultravox] Disconnected")

    # ------------------------------------------------------------------
    # Frame handling
    # ------------------------------------------------------------------

    async def process_frame(self, frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        logger.debug(f"[Ultravox] process_frame received: {type(frame).__name__}")

        # On pipeline start, connect eagerly
        if isinstance(frame, StartFrame):
            await self._ensure_connected()
            await self.push_frame(frame, direction)

        elif isinstance(frame, (EndFrame, CancelFrame)):
            await self._disconnect()
            await self.push_frame(frame, direction)

        elif isinstance(frame, (UserStartedSpeakingFrame, VADUserStartedSpeakingFrame)):
            self._audio_buffer = []
            self._collecting = True
            logger.debug("[Ultravox] User started speaking — buffering audio")
            await self.push_frame(frame, direction)

        elif isinstance(frame, AudioRawFrame) and self._collecting:
            pcm = np.frombuffer(frame.audio, dtype=np.int16)
            self._audio_buffer.append(pcm)
            # Don't push audio downstream — TTS will handle output

        elif isinstance(frame, (UserStoppedSpeakingFrame, VADUserStoppedSpeakingFrame)):
            self._collecting = False
            logger.debug("[Ultravox] User stopped speaking — sending audio")
            await self.push_frame(frame, direction)

            if self._audio_buffer:
                await self._send_and_stream()
            else:
                logger.warning("[Ultravox] No audio buffered, skipping send")

        else:
            await self.push_frame(frame, direction)


    # ------------------------------------------------------------------
    # Send audio to server and stream response
    # ------------------------------------------------------------------

    async def _send_and_stream(self):
        # Reconnect if needed
        ok = await self._ensure_connected()
        if not ok:
            logger.error("[Ultravox] Cannot send — not connected")
            return

        # Encode audio
        audio_np = np.concatenate(self._audio_buffer)
        audio_b64 = base64.b64encode(audio_np.tobytes()).decode("utf-8")
        request_id = str(uuid.uuid4())

        generate_msg = {
            "type": "generate",
            "request_id": request_id,
            "caller_id": self._caller_id,
            "audio_data": audio_b64,
            "messages": [{"role": "user", "content": "<|audio|>\n"}],
            "temperature": 0.2,
            "max_tokens": 500,
        }

        try:
            await self._ws.send(json.dumps(generate_msg))
        except Exception as e:
            logger.error(f"[Ultravox] Failed to send generate message: {e}")
            self._connected = False
            return

        await self.push_frame(LLMFullResponseStartFrame())

        full_text = ""
        try:
            async for raw in self._ws:
                msg = json.loads(raw)
                mtype = msg.get("type")

                if mtype == "started":
                    logger.debug(f"[Ultravox:{request_id}] Generation started")

                elif mtype == "partial":
                    chunk = msg.get("text", "")
                    if chunk:
                        full_text += chunk
                        await self.push_frame(TextFrame(text=chunk))

                elif mtype == "completed":
                    # Server may send remaining text in completed
                    remaining = msg.get("text", "")
                    if remaining and remaining not in full_text:
                        await self.push_frame(TextFrame(text=remaining))
                    logger.info(f"[Ultravox:{request_id}] Completed — response: {full_text[:80]}...")
                    break

                elif mtype == "error":
                    logger.error(f"[Ultravox:{request_id}] Server error: {msg.get('error')}")
                    break

                elif mtype == "cancelled":
                    logger.info(f"[Ultravox:{request_id}] Cancelled")
                    break

        except ConnectionClosed as e:
            logger.warning(f"[Ultravox] Connection closed during streaming: {e}")
            self._connected = False

        except Exception as e:
            logger.error(f"[Ultravox] Streaming error: {e}")
            self._connected = False

        finally:
            await self.push_frame(LLMFullResponseEndFrame())