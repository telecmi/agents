# Copyright (c) 2025-2026, TeleCMI
# SPDX-License-Identifier: BSD-2-Clause

import json
import uuid
import asyncio
import logging
from contextlib import suppress
from typing import AsyncGenerator, Optional, Union, Any

from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, ConnectionClosedError

from piopiy.frames.frames import (
    Frame,
    TTSStartedFrame,
    TTSAudioRawFrame,
    TTSStoppedFrame,
    ErrorFrame,
    StartInterruptionFrame,
    CancelFrame,
    EndFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.tts_service import InterruptibleTTSService


logger = logging.getLogger(__name__)


class ChatterboxTTSService(InterruptibleTTSService):
    """
    Interruptible TTS wrapper for Chatterbox WS server.

    Protocol:
      - Send:   {"type":"synthesize","text":...,"voice":?,"request_id":...}
      - Stream: binary PCM s16le frames
      - Ctrl:   {"type":"started", ...}, {"type":"done", ...}, {"type":"error", ...}
      - Cancel: {"type":"cancel","request_id":...}
    """

    def __init__(
        self,
        *,
        base_url: str = "ws://localhost:60007",
        voice: Optional[str] = None,
        sample_rate: int = 24000,
        request_timeout_s: float = 65.0,
        reuse_socket: bool = True,
        hard_cancel_on_interrupt: bool = False,
        **kwargs,
    ):
        super().__init__(
            sample_rate=sample_rate,
            push_stop_frames=True,
            pause_frame_processing=True,
            **kwargs,
        )
        self._base_url = base_url
        if voice:
            self.set_voice(voice)

        self._ws: Optional[Any] = None
        self._timeout = float(request_timeout_s)

        self._reuse_socket = bool(reuse_socket)
        self._hard_cancel_on_interrupt = bool(hard_cancel_on_interrupt)

        self._stop_event = asyncio.Event()
        self._was_interrupted = False

        # Prevent overlapping run_tts() calls
        self._synth_lock = asyncio.Lock()
        self._speaking = False

        # Track request_id for targeted cancel
        self._current_req_id: Optional[str] = None

    # -------------
    # Piopiy hooks
    # -------------
    async def push_frame(self, frame: Frame, direction: FrameDirection = FrameDirection.DOWNSTREAM):
        if isinstance(frame, StartInterruptionFrame):
            if self._hard_cancel_on_interrupt:
                self._reuse_socket = False
            logger.debug("push_frame: StartInterruptionFrame")
            await self.interrupt()
        elif isinstance(frame, (CancelFrame, EndFrame)):
            self._reuse_socket = False
            logger.debug("push_frame: %s -> interrupt (reuse_socket=False)", type(frame).__name__)
            await self.interrupt()
        return await super().push_frame(frame, direction)

    # -------------
    # WS plumbing
    # -------------
    async def _connect_websocket(self) -> bool:
        if self._ws is not None and not getattr(self._ws, "closed", False):
            return True
        self._ws = await ws_connect(self._base_url, max_size=None)
        return True

    async def _disconnect_websocket(self) -> None:
        ws = self._ws
        self._ws = None
        if ws and not getattr(ws, "closed", False):
            with suppress(Exception):
                await ws.close()

    async def _connect(self) -> bool:
        return await self._connect_websocket()

    async def _disconnect(self) -> None:
        await self._disconnect_websocket()

    async def _receive_messages(self) -> AsyncGenerator[Union[bytes, str], None]:
        if not self._ws:
            return
        try:
            async for msg in self._ws:
                yield msg
        except Exception:
            return

    # -------------
    # Interruption
    # -------------
    async def interrupt(self) -> None:
        self._stop_event.set()
        self._was_interrupted = True

        ws = self._ws
        if ws:
            with suppress(Exception):
                if self._current_req_id:
                    await ws.send(json.dumps({"type": "cancel", "request_id": self._current_req_id}))
                else:
                    await ws.send(json.dumps({"type": "cancel"}))

            if not self._reuse_socket:
                with suppress(Exception):
                    await ws.close()
                self._ws = None

    async def _drain_after_cancel(self, timeout_s: float = 0.2) -> None:
        ws = self._ws
        if not ws or not self._reuse_socket:
            return

        loop = asyncio.get_event_loop()
        deadline = loop.time() + float(timeout_s)

        while loop.time() < deadline:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=max(0.01, deadline - loop.time()))
            except (asyncio.TimeoutError, ConnectionClosedOK, ConnectionClosedError, ConnectionClosed):
                break
            except Exception:
                break

            if isinstance(msg, str):
                try:
                    j = json.loads(msg)
                    if j.get("type") == "done" and j.get("request_id") == self._current_req_id:
                        break
                except Exception:
                    pass

    # -------------
    # Main speak
    # -------------
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        async with self._synth_lock:
            self._stop_event.clear()
            self._was_interrupted = False
            self._speaking = True
            req_id = f"req-{uuid.uuid4()}"
            self._current_req_id = req_id
            announced_sr = self.sample_rate
            ttfb_stopped = False
            stopped_yielded = False
            synthesis_started = False

            stop_task: Optional[asyncio.Task] = asyncio.create_task(self._stop_event.wait())

            try:
                ok = await self._connect_websocket()
                if not ok or self._ws is None:
                    yield ErrorFrame("WS connect failed")
                    return

                await self.start_ttfb_metrics()
                await self.start_tts_usage_metrics(text)
                yield TTSStartedFrame()

                await self._ws.send(json.dumps({
                    "type": "synthesize",
                    "text": text,
                    "voice": getattr(self, "_voice_id", None),
                    "request_id": req_id,
                }))

                while True:
                    recv_task = asyncio.create_task(self._ws.recv())
                    done, pending = await asyncio.wait(
                        {recv_task, stop_task},
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=self._timeout,
                    )

                    if not done:
                        recv_task.cancel()
                        with suppress(asyncio.CancelledError, ConnectionClosedOK, ConnectionClosedError, ConnectionClosed):
                            await recv_task

                        if self._was_interrupted:
                            if not stopped_yielded:
                                yield TTSStoppedFrame()
                                stopped_yielded = True
                            break
                        yield ErrorFrame("TTS timeout")
                        break

                    if stop_task in done:
                        recv_task.cancel()
                        with suppress(asyncio.CancelledError):
                            await recv_task
                        if not stopped_yielded:
                            yield TTSStoppedFrame()
                            stopped_yielded = True
                        await self._drain_after_cancel(0.2)
                        break

                    try:
                        msg = recv_task.result()
                    except (ConnectionClosedOK, ConnectionClosedError, ConnectionClosed) as e:
                        if self._was_interrupted and not stopped_yielded:
                            yield TTSStoppedFrame()
                            stopped_yielded = True
                        else:
                            yield ErrorFrame(f"WS closed: {e}")
                        break
                    except Exception as e:
                        if self._was_interrupted and not stopped_yielded:
                            yield TTSStoppedFrame()
                            stopped_yielded = True
                        else:
                            yield ErrorFrame(f"Chatterbox WS TTS error: {e}")
                        break

                    if isinstance(msg, (bytes, bytearray)):
                        if self._stop_event.is_set():
                            logger.debug("run_tts: drop PCM after interrupt")
                            break
                        if not synthesis_started:
                            logger.debug("run_tts: drop PCM before started")
                            continue
                        if not ttfb_stopped:
                            ttfb_stopped = True
                            with suppress(Exception):
                                await self.stop_ttfb_metrics()
                        yield TTSAudioRawFrame(audio=bytes(msg), sample_rate=announced_sr, num_channels=1)
                        continue

                    try:
                        j = json.loads(msg) if isinstance(msg, str) else {}
                    except Exception:
                        continue

                    t = j.get("type")
                    req_id_received = j.get("request_id")
                    if req_id_received != self._current_req_id:
                        continue

                    if t == "started":
                        sr = j.get("sample_rate")
                        if sr is not None:
                            with suppress(Exception):
                                announced_sr = int(sr)
                        synthesis_started = True
                        if self._stop_event.is_set():
                            with suppress(Exception):
                                await self._ws.send(json.dumps({"type": "cancel", "request_id": req_id}))
                            break
                    elif t == "error":
                        yield ErrorFrame(str(j.get("error")))
                        break
                    elif t == "done":
                        break

                if not stopped_yielded:
                    yield TTSStoppedFrame()
                    stopped_yielded = True

            except Exception as e:
                yield ErrorFrame(f"Chatterbox WS TTS error: {e}")

            finally:
                with suppress(Exception):
                    if not ttfb_stopped:
                        await self.stop_ttfb_metrics()
                with suppress(Exception):
                    await self.stop_tts_usage_metrics()
                if stop_task and not stop_task.done():
                    stop_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await stop_task
                if not self._reuse_socket:
                    await self._disconnect_websocket()
                self._speaking = False
                self._current_req_id = None