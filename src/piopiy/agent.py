# Copyright (c) 2024-2026, TeleCMI
# SPDX-License-Identifier: BSD 2-Clause License

import asyncio
import inspect
import json
import logging
import signal
import sys
from contextvars import ContextVar
from typing import Any, Awaitable, Callable, Dict, Optional

import socketio

URL_CTX: ContextVar[str] = ContextVar("telecmi_url")
TOKEN_CTX: ContextVar[str] = ContextVar("telecmi_token")
ROOM_CTX: ContextVar[str] = ContextVar("telecmi_room")

logger = logging.getLogger(__name__)

try:
    from .config import SIGNALING_URL as DEFAULT_SIGNALING_URL
except ImportError:
    DEFAULT_SIGNALING_URL = "https://signaling.piopiy.com"


def _parse_metadata(raw: Any) -> Any:
    """Parse the metadata field from a join_room invite.

    Producers may send metadata as a dict, a JSON string, or (occasionally) a
    double-encoded JSON string with stray escapes. Return whatever we can
    decode; fall back to the raw value if decoding fails.
    """
    if raw is None:
        return None
    if not isinstance(raw, str):
        return raw

    # Some producers escape closing braces.
    candidate = raw.replace(r"\}", "}") if r"\}" in raw else raw
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return raw

    # Handle double-encoded JSON ("\"{\\\"k\\\":\\\"v\\\"}\"").
    if isinstance(parsed, str):
        try:
            return json.loads(parsed)
        except json.JSONDecodeError:
            return parsed
    return parsed


class Agent:
    """TeleCMI signaling client.

    Connects to the TeleCMI signaling endpoint over Socket.IO and dispatches
    each incoming ``join_room`` event to the user-supplied
    ``create_session`` coroutine. ``create_session`` receives whichever of
    ``call_id``, ``agent_id``, ``from_number``, ``to_number``, and ``metadata``
    its signature accepts.
    """

    def __init__(
        self,
        agent_id: str,
        agent_token: str,
        create_session: Callable[..., Awaitable[None]],
        signaling_url: Optional[str] = None,
        debug: bool = False,
    ) -> None:
        self.signaling_url = signaling_url or DEFAULT_SIGNALING_URL
        self.agent_id = agent_id
        self.agent_token = agent_token
        self.create_session = create_session
        self.debug = debug

        self._configure_logging()

        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.active_sessions: Dict[str, asyncio.Task] = {}

        self._setup_events()

    def _configure_logging(self) -> None:
        """Configure logging for the agent.

        Libraries normally shouldn't touch root logging, but ``debug=True``
        is an explicit opt-in by the user so we honour it. With ``debug=False``
        we leave the root logger alone and just silence a few noisy
        third-party loggers.
        """
        if self.debug:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            )
            try:
                from loguru import logger as loguru_logger

                loguru_logger.remove()
                loguru_logger.add(sys.stderr, level="INFO")
            except ImportError:
                pass
        else:
            for name in ("deepgram", "asyncio", "websockets"):
                logging.getLogger(name).setLevel(logging.CRITICAL)

    def _setup_events(self) -> None:
        @self.sio.event
        async def connect() -> None:
            logger.info("Connected to signaling as agent %s", self.agent_id)

        @self.sio.on("join_room")
        async def handle_join_session(invite: dict) -> None:
            room = invite.get("room_name")
            token = invite.get("token")
            url = invite.get("url") or self.signaling_url

            if not room or not token:
                logger.warning("Invalid join_room payload: %s", invite)
                return

            existing = self.active_sessions.get(room)
            if existing and not existing.done():
                logger.warning("Session %s already running", room)
                return

            async def session_runner() -> None:
                tok_url = URL_CTX.set(url)
                tok_token = TOKEN_CTX.set(token)
                tok_room = ROOM_CTX.set(room)
                try:
                    sig = inspect.signature(self.create_session)
                    kwargs: Dict[str, Any] = {}
                    if "call_id" in sig.parameters:
                        kwargs["call_id"] = invite.get("call_id")
                    if "agent_id" in sig.parameters:
                        kwargs["agent_id"] = invite.get("agent_id")
                    if "from_number" in sig.parameters:
                        kwargs["from_number"] = invite.get("from_number")
                    if "to_number" in sig.parameters:
                        kwargs["to_number"] = invite.get("to_number")
                    if "metadata" in sig.parameters:
                        kwargs["metadata"] = _parse_metadata(invite.get("metadata"))

                    if self.debug:
                        logger.info("join_room invite payload: %s", invite)

                    await self.create_session(**kwargs)
                finally:
                    ROOM_CTX.reset(tok_room)
                    TOKEN_CTX.reset(tok_token)
                    URL_CTX.reset(tok_url)

            task = asyncio.create_task(session_runner(), name=f"session:{room}")
            self.active_sessions[room] = task
            task.add_done_callback(lambda _t: self.active_sessions.pop(room, None))

        @self.sio.on("cancel_room")
        async def handle_cancel_session(data: dict) -> None:
            room = data.get("room_name")
            if not room:
                return
            task = self.active_sessions.pop(room, None)
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def connect(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        await self.sio.connect(
            self.signaling_url,
            auth={"agent_id": self.agent_id, "token": self.agent_token},
        )
        try:
            await self.sio.wait()
        except asyncio.CancelledError:
            pass

    async def shutdown(self) -> None:
        logger.info("Shutting down agent...")

        try:
            await self.sio.disconnect()
        except Exception as exc:  # noqa: BLE001 — best-effort cleanup on shutdown
            logger.debug("Error during socket disconnect: %s", exc)

        tasks = list(self.active_sessions.values())
        self.active_sessions.clear()
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Agent shutdown complete.")
