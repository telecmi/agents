# Copyright (c) 2025-2026, TeleCMI
# SPDX-License-Identifier: BSD-2-Clause

import json
import uuid
import asyncio
from contextlib import suppress
from typing import AsyncGenerator, Optional, Union

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


class OrpheusTTS(InterruptibleTTSService):
    """
    Interruptible TTS wrapper for Orpheus WS server.

    Protocol:
      - Send:   {"type":"synthesize","text":...,"voice":?,"request_id":...}
      - Stream: binary PCM s16le frames
      - Ctrl:   {"type":"started", ...}, {"type":"done", ...}
      - Cancel: {"type":"cancel"}
    """

    def __init__(
        self,
        *,
        base_url: str = "ws://127.0.0.1:8765",
        voice: Optional[str] = None,
        sample_rate: int = 24000,
        request_timeout_s: float = 65.0,
        reuse_socket: bool = True,  # graceful by default
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

        self._ws = None  # type: Optional[any]
        self._timeout = float(request_timeout_s)

        self._reuse_socket = bool(reuse_socket)
        self._stop_event = asyncio.Event()
        self._was_interrupted = False

        # Prevent overlapping run_tts() calls from this instance
        self._synth_lock = asyncio.Lock()
        self._speaking = False

    # -------------
    # Piopiy hooks
    # -------------
    async def push_frame(self, frame: Frame, direction: FrameDirection = FrameDirection.DOWNSTREAM):
        if isinstance(frame, StartInterruptionFrame):
            self._was_interrupted = True
        elif isinstance(frame, (CancelFrame, EndFrame)):
            # End the transport fully
            self._reuse_socket = False
        return await super().push_frame(frame, direction)

    # -------------
    # WS plumbing
    # -------------
    async def _connect_websocket(self) -> bool:
        if self._ws is not None:
            return True
        self._ws = await ws_connect(self._base_url, max_size=None)
        return True

    async def _disconnect_websocket(self) -> None:
        ws = self._ws
        self._ws = None
        if ws:
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
        """Barge-in: send cancel; either keep or close WS."""
        self._stop_event.set()
        self._was_interrupted = True

        ws = self._ws
        if ws:
            with suppress(Exception):
                await ws.send(json.dumps({"type": "cancel"}))

            if not self._reuse_socket:
                with suppress(Exception):
                    await ws.close()
                self._ws = None

    # -------------
    # Main speak
    # -------------
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """
        Yields: TTSStartedFrame, TTSAudioRawFrame(...)*, TTSStoppedFrame or ErrorFrame
        """
        async with self._synth_lock:  # prevent overlapping run_tts() from this instance
            self._stop_event.clear()
            self._was_interrupted = False
            self._speaking = True
            req_id = f"req-{uuid.uuid4()}"
            announced_sr = self.sample_rate
            ttfb_stopped = False

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

                async def recv_one():
                    return await asyncio.wait_for(self._ws.recv(), timeout=self._timeout)

                while True:
                    try:
                        msg = await recv_one()
                    except asyncio.TimeoutError:
                        if self._was_interrupted:
                            break
                        yield ErrorFrame("TTS timeout")
                        break
                    except (ConnectionClosedOK, ConnectionClosedError, ConnectionClosed) as e:
                        if self._was_interrupted:
                            break
                        yield ErrorFrame(f"WS closed: {e}")
                        break
                    except Exception as e:
                        if self._was_interrupted:
                            break
                        yield ErrorFrame(f"Orpheus WS TTS error: {e}")
                        break

                    # Binary PCM
                    if isinstance(msg, (bytes, bytearray)):
                        # In graceful mode: drop any late frames after cancel
                        if self._stop_event.is_set() and self._reuse_socket:
                            continue
                        if not ttfb_stopped:
                            ttfb_stopped = True
                            with suppress(Exception):
                                await self.stop_ttfb_metrics()
                        yield TTSAudioRawFrame(
                            audio=bytes(msg),
                            sample_rate=announced_sr,
                            num_channels=1,
                        )
                        continue

                    # Control JSON
                    try:
                        j = json.loads(msg) if isinstance(msg, str) else {}
                    except Exception:
                        continue

                    t = j.get("type")
                    if t == "started":
                        sr = j.get("sample_rate")
                        if sr is not None:
                            with suppress(Exception):
                                announced_sr = int(sr)
                    elif t == "error":
                        # surface server errors (should be rare now that server auto-cancels)
                        yield ErrorFrame(str(j.get("error")))
                        break
                    elif t == "done":
                        break
                    else:
                        continue

                yield TTSStoppedFrame()

            except Exception as e:
                yield ErrorFrame(f"Orpheus WS TTS error: {e}")

            finally:
                with suppress(Exception):
                    if not ttfb_stopped:
                        await self.stop_ttfb_metrics()
                if not self._reuse_socket:
                    await self._disconnect_websocket()
                self._speaking = False
