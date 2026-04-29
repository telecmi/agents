"""Speech-to-Speech voice agent using Grok Realtime (xAI).

Grok Realtime supports bidirectional audio streaming, function calling,
and built-in tools (web_search, x_search, file_search).

Requirements:
    pip install "piopiy-ai[grok,silero]"

Environment:
    AGENT_ID, AGENT_TOKEN
    XAI_API_KEY
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.grok.realtime import events
from piopiy.services.grok.realtime.llm import GrokRealtimeLLMService
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 Grok Realtime call {call_id}: {from_number} → {to_number}")

    voice_agent = VoiceAgent(
        instructions=(
            "You are a witty voice assistant with access to web search. "
            "Keep replies short and conversational."
        ),
        greeting="Hi! This is Grok. What's on your mind?",
    )

    llm = GrokRealtimeLLMService(
        api_key=os.environ["XAI_API_KEY"],
        session_properties=events.SessionProperties(
            voice="Rex",     # Ara | Rex | Sal | Eve | Leo
        ),
    )

    # Speech-to-speech: no stt, no tts.
    await voice_agent.configure(llm=llm, allow_interruptions=True)
    await voice_agent.start()


async def main():
    if not os.getenv("XAI_API_KEY"):
        raise SystemExit("❌ XAI_API_KEY is not set")

    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )
    print("🚀 Grok Realtime agent — waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
