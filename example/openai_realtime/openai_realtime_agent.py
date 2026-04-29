"""Speech-to-Speech voice agent using OpenAI Realtime.

OpenAI Realtime (gpt-realtime / gpt-4o-realtime-preview) consumes user audio
and emits agent audio directly. No separate STT/TTS — `voice_agent.configure(llm=...)`
with no `tts=` puts the agent in speech-to-speech mode.

Requirements:
    pip install "piopiy-ai[openai,silero]"

Environment:
    AGENT_ID, AGENT_TOKEN
    OPENAI_API_KEY
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.openai.realtime import events
from piopiy.services.openai.realtime.llm import OpenAIRealtimeLLMService
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 OpenAI Realtime call {call_id}: {from_number} → {to_number}")

    voice_agent = VoiceAgent(
        instructions="You are a friendly voice assistant. Keep replies concise.",
        greeting="Hi! This is OpenAI Realtime. How can I help?",
    )

    llm = OpenAIRealtimeLLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-realtime",
        session_properties=events.SessionProperties(
            voice="alloy",                   # alloy, echo, fable, onyx, nova, shimmer, coral, verse
            instructions=(
                "You are a friendly voice assistant. "
                "Keep responses under two short sentences."
            ),
            temperature=0.8,
        ),
    )

    # No `stt`, no `tts` — speech-to-speech mode.
    await voice_agent.configure(llm=llm, allow_interruptions=True)
    await voice_agent.start()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("❌ OPENAI_API_KEY is not set")

    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )
    print("🚀 OpenAI Realtime agent — waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
