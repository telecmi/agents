# agent.py
# Copyright (c) 2024–2025, TeleCMI
# SPDX-License-Identifier: BSD 2-Clause License

import asyncio
import logging
import signal
from typing import Awaitable, Callable, Dict, Optional
from contextvars import ContextVar
import socketio

URL_CTX: ContextVar[str] = ContextVar("telecmi_url")
TOKEN_CTX: ContextVar[str] = ContextVar("telecmi_token")
ROOM_CTX: ContextVar[str] = ContextVar("telecmi_room")


logger = logging.getLogger(__name__)

try:
    from .config import SIGNALING_URL as DEFAULT_SIGNALING_URL
except Exception:
    # Fallback if config import isn't available
    DEFAULT_SIGNALING_URL = "https://signaling.piopiy.com"
 

class Agent:
    def __init__(
        self,
        agent_id: str,
        agent_token: str,
        create_session: Callable[[str, str, str], Awaitable[None]],
        signaling_url: Optional[str] = None,
    ):
        """
        create_session(url, token, room_name) -> coroutine
        """
        self.signaling_url = signaling_url or DEFAULT_SIGNALING_URL
        self.agent_id = agent_id
        self.agent_token = agent_token
        self.create_session = create_session

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.active_sessions: Dict[str, asyncio.Task] = {}

        self._setup_events()

    def _setup_events(self) -> None:
        @self.sio.event
        async def connect():
            logger.info("Connected to signaling as agent %s", self.agent_id)

        @self.sio.on("join_room")
        async def handle_join_session(invite: dict):
            room = invite.get("room_name")
            token = invite.get("token")
            # Typically the controller gives you the LiveKit/TeleCMI URL here
            url = invite.get("url") or self.signaling_url

            if not room or not token:
                logger.warning("Invalid join_room payload: %s", invite)
                return

            # avoid running two sessions for the same room
            existing = self.active_sessions.get(room)
            if existing and not existing.done():
                logger.warning("Session %s already running", room)
                return
            
            tok_url = URL_CTX.set(url)
            tok_token = TOKEN_CTX.set(token)
            tok_room = ROOM_CTX.set(room)
            
            try:
                task = asyncio.create_task(
                    self.create_session(),  # zero-arg; will read ContextVars
                    name=f"session:{room}",
                )
            finally:
                # Reset in reverse order (good hygiene)
                ROOM_CTX.reset(tok_room)
                TOKEN_CTX.reset(tok_token)
                URL_CTX.reset(tok_url)

           
            self.active_sessions[room] = task

            # remove from registry when it finishes (success or error)
            task.add_done_callback(lambda _: self.active_sessions.pop(room, None))

        @self.sio.on("cancel_room")
        async def handle_cancel_session(data: dict):
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

        # 1) stop receiving new join_room events
        try:
            await self.sio.disconnect()
        except Exception:
            pass

        # 2) cancel any active room tasks
        tasks = list(self.active_sessions.values())
        self.active_sessions.clear()
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Agent shutdown complete.")
