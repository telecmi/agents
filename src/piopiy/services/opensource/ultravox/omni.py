#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pipecat client service for Ultravox LLM over WebSocket (audio → streamed text)."""

import asyncio
import base64
import json
import time
import uuid
import sys
from typing import AsyncGenerator, Dict, List, Optional

import numpy as np
import websockets
from loguru import logger
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK

from piopiy.frames.frames import (
    AudioRawFrame,
    CancelFrame,
    EndFrame,
    ErrorFrame,
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    StartFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.ai_service import AIService
from piopiy.transcriptions.language import Language
from piopiy.utils.time import time_now_iso8601

class _Buf:
    def __init__(self):
        self.frames: List[AudioRawFrame] = []
        self.started_at: Optional[float] = None
        self.processing: bool = False

class UltravoxService(AIService):
    """
    Client that sends buffered audio to the uvx LLM server and streams text back.
    Downstream TTS will speak the streamed LLMTextFrame.
    """

    def __init__(
        self,
        *,
        server_url: str = "ws://localhost:8766",
        language: Language = Language.EN,
        temperature: float = 0.2,
        max_tokens: int = 200,
        system_prompt: Optional[str] = None,
        persistent_connection: bool = True,
        ping_interval: float = 20.0,
        ping_timeout: float = 20.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._url = server_url
        self._lang = language
        self._temp = temperature
        self._max_tokens = max_tokens
        self._sys = system_prompt
        self._persist = persistent_connection
        self._ping_i = ping_interval
        self._ping_t = ping_timeout

        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._lock = asyncio.Lock()
        self._buf = _Buf()
        self._inflight: Dict[str, asyncio.Event] = {}

    def can_generate_metrics(self) -> bool:
        return True

    async def disconnet_client(self, caller_id: Optional[str] = 123456789):
        if caller_id is None:
            return
        try:
            logger.info(f"Disconnecting client {caller_id} from Ultravox server")
        except Exception as e:
            logger.warning(f"Failed to disconnect client {caller_id}: {e}")

    async def transfer_client(self, caller_id: Optional[str] = 123456789):
        if caller_id is None:
            return
        try:
            logger.info(f"Tranfering client {caller_id} to real agent from Ultravox server")
        except Exception as e:
            logger.warning(f"Failed to disconnect client {caller_id}: {e}")

    async def start(self, frame: StartFrame):
        await super().start(frame)
        if self._persist:
            await self._connect()

    async def stop(self, frame: EndFrame):
        await super().stop(frame)
        await self._flush()
        await self._disconnect()

    async def cancel(self, frame: CancelFrame):
        await super().cancel(frame)
        await self._cancel_all()
        await self._disconnect()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStartedSpeakingFrame):
            self._buf = _Buf()
            self._buf.started_at = time.time()

        elif isinstance(frame, AudioRawFrame) and self._buf.started_at is not None:
            self._buf.frames.append(frame)

        elif isinstance(frame, UserStoppedSpeakingFrame):
            if self._buf.frames and not self._buf.processing:
                await self.process_generator(self._process_audio_buffer())
                return

        if frame is not None:
            await self.push_frame(frame, direction)

    # ------------------ internals ------------------

    async def _connect(self):
        if self._ws and not self._ws.closed:
            return
        async with self._lock:
            if self._ws and not self._ws.closed:
                return
            self._ws = await websockets.connect(
                self._url, ping_interval=self._ping_i, ping_timeout=self._ping_t, max_size=None
            )

    async def _disconnect(self):
        async with self._lock:
            if self._ws and not self._ws.closed:
                try:
                    await self._ws.close()
                except Exception:
                    pass
            self._ws = None

    async def _ensure(self):
        if not self._persist:
            await self._connect()
            return
        if not self._ws or self._ws.closed:
            await self._connect()

    async def _send_json(self, payload: dict):
        await self._ensure()
        assert self._ws is not None
        await self._ws.send(json.dumps(payload))

    async def _flush(self):
        if self._buf.frames and not self._buf.processing:
            await self.process_generator(self._process_audio_buffer())

    async def _cancel_all(self):
        for rid, evt in list(self._inflight.items()):
            try:
                await self._send_json({"type":"cancel","request_id": rid})
            except Exception:
                pass
            finally:
                evt.set()
                self._inflight.pop(rid, None)

    async def _process_audio_buffer(self) -> AsyncGenerator[Frame, None]:
        try:
            self._buf.processing = True

            # gather audio int16 PCM
            chunks = []
            for f in self._buf.frames:
                if isinstance(f.audio, bytes):
                    arr = np.frombuffer(f.audio, dtype=np.int16)
                elif isinstance(f.audio, np.ndarray):
                    arr = f.audio.astype(np.int16) if f.audio.dtype != np.int16 else f.audio
                else:
                    arr = None
                if arr is not None and arr.size:
                    chunks.append(arr)

            if not chunks:
                yield ErrorFrame("No valid audio")
                return

            audio_int16 = np.concatenate(chunks)
            audio_b64 = base64.b64encode(audio_int16.tobytes()).decode("utf-8")

            # build messages
            messages = []
            if self._sys:
                messages.append({"role":"system","content": self._sys})

            messages.append({"role":"user","content":"<|audio|>\n"})

            rid = f"uvx-{uuid.uuid4()}"
            req = {
                "type": "generate",
                "request_id": rid,
                "audio_data": audio_b64,
                "language": self._lang.value,
                "temperature": self._temp,
                "max_tokens": self._max_tokens,
                "messages": messages,
            }

            # metrics
            await self.start_ttfb_metrics()
            await self.start_processing_metrics()

            # tell downstream TTS a response is starting
            yield LLMFullResponseStartFrame()

            done = asyncio.Event()
            self._inflight[rid] = done

            # send
            await self._send_json(req)

            # ---------- FIX for cumulative text issue ----------
            previous_text = ""
            # ---------- FIX for cumulative text issue ----------

            # receive loop (non-persistent is also supported)
            while True:
                if not self._persist:
                    await self._ensure()
                assert self._ws is not None
                raw = await self._ws.recv()
                data = json.loads(raw)
                mtype = data.get("type")
                if mtype == "started":
                    # wait for first token to stop TTFB
                    pass
                elif mtype == "partial":
                    # first arrival => stop TTFB
                    await self.stop_ttfb_metrics()

                    text = (data.get("text") or "").strip()
                    text = text.replace("function_call","")  
                    cumulative_text = text

                    # Compute the delta (new text only)
                    if cumulative_text.startswith(previous_text):
                        delta = cumulative_text[len(previous_text):]
                    else:
                        # Fallback if text doesn't build cumulatively (shouldn't happen)
                        delta = cumulative_text
                    
                    previous_text = cumulative_text
                    if  "function_call" not in delta and delta:
                        
                    # Only yield if there's new text
                    # if delta:
                        yield LLMTextFrame(text=delta)
                    # ---------- FIX for cumulative text issue ----------
                elif mtype == "completed":
                    await self.stop_processing_metrics()
                    # text = (data.get("text") or "").strip()
                    # if text:
                    #     # final flush already sent in partials; nothing extra needed
                    #     pass
                    # yield LLMFullResponseEndFrame()
                    # done.set()
                    # break

                    # ---------- FIX for cumulative text issue ----------
                    # Get final text
                    final_text = (data.get("text") or "").strip()
                    
                    yield  LLMTextFrame(text=final_text)
                    # Check if there's any remaining text not yet sent
                    # if final_text.startswith(previous_text):
                    #     delta = final_text[len(previous_text):]
                    #     if delta:
                    #         yield LLMTextFrame(text=delta)
                    
                    yield LLMFullResponseEndFrame()
                    done.set()
                    break
                    # ---------- FIX for cumulative text issue ----------
                elif mtype == "error":
                    await self.stop_processing_metrics()
                    yield ErrorFrame(f"Ultravox LLM error: {data.get('error')}")
                    yield LLMFullResponseEndFrame()
                    done.set()
                    break
                elif mtype == "cancelled":
                    await self.stop_processing_metrics()
                    yield LLMFullResponseEndFrame()
                    done.set()
                    break
                elif mtype == "disconnect":
                    logger.info(f"###########Received disconnect command from server: {data}")
                    await self.stop_processing_metrics()
                    text = data["text"]
                    yield LLMTextFrame(text=text)
                    yield LLMFullResponseEndFrame()
                    done.set()
                    await self._disconnect()
                    await self.disconnet_client()
                    break

                elif mtype == "transfer":
                    logger.info(f"###########Received tranfer command from server: {data}")
                    await self.stop_processing_metrics()
                    text = data["text"]
                    yield LLMTextFrame(text=text)
                    yield LLMFullResponseEndFrame()
                    done.set()
                    await self._disconnect()
                    await self.transfer_client()
                    break
                
            # if non-persistent, close after each call
            if not self._persist:
                await self._disconnect()

        except (ConnectionClosed, ConnectionClosedError, ConnectionClosedOK):
            yield ErrorFrame("Connection closed")
            yield LLMFullResponseEndFrame()
        except Exception as e:
            logger.exception(e)
            yield ErrorFrame(f"Client processing error: {e}")
            yield LLMFullResponseEndFrame()
        finally:
            self._buf.processing = False
            self._buf.frames = []
            self._buf.started_at = None