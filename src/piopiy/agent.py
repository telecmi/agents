#
# Copyright (c) 2024–2025, TeleCMI
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import signal
import logging
import socketio
from typing import Callable, Awaitable
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variables for current session
current_room: ContextVar[str] = ContextVar('current_room')
current_token: ContextVar[str] = ContextVar('current_token')
current_url: ContextVar[str] = ContextVar('current_url')

try:
    from .config import SIGNALING_URL as DEFAULT_SIGNALING_URL
except ImportError:
    from config import SIGNALING_URL as DEFAULT_SIGNALING_URL  # if agent.py is alongside config.py


class Agent:
    def __init__(
        self,
        agent_id: str,
        agent_token: str,
        create_session: Callable[[], Awaitable],
         signaling_url: str | None = None, 
    ):
        self.signaling_url = signaling_url or DEFAULT_SIGNALING_URL
        self.agent_id = agent_id
        self.agent_token = agent_token
        self.create_session = create_session

        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.active_sessions = {}

        self._setup_events()

    def _setup_events(self):
        @self.sio.event
        async def connect():
            logger.info("Connected to signaling as agent %s", self.agent_id)

        @self.sio.on("join_room")
        async def handle_join_session(invite: dict):
            room = invite["room_name"]
            token = invite["token"]
            url = invite["url"]
         
            if room in self.active_sessions:
                logger.warning(f"Session {room} already running")
                return

            logger.info(f"Creating session for room: {room}")
            
            # Set session context
            current_room.set(room)
            current_token.set(token)
            current_url.set(url)
            
            # Create session
            session_coro = self.create_session()
            task = asyncio.create_task(session_coro)
            self.active_sessions[room] = task

            def cleanup(_):
                self.active_sessions.pop(room, None)
            task.add_done_callback(cleanup)

        @self.sio.on("cancel_room")
        async def handle_cancel_session(data: dict):
            room = data["room_name"]
            task = self.active_sessions.get(room)
            if task and not task.done():
                task.cancel()
            self.active_sessions.pop(room, None)

    async def start(self):
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

    async def shutdown(self):
        logger.info("Shutting down agent...")
        await self.sio.disconnect()

        for task in self.active_sessions.values():
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.active_sessions.values(), return_exceptions=True)

        pending = [t for t in asyncio.all_tasks() if not t.done()]
        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        logger.info("Agent shutdown complete.")