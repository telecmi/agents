"""Speech-to-Speech voice agent using Gemini Live.

Gemini Live consumes user audio and emits agent audio directly. There is no
separate STT or TTS stage — just configure `VoiceAgent` with `llm=` only.

Requirements:
    pip install "piopiy-ai[google,silero]"

Environment variables:
    AGENT_ID, AGENT_TOKEN
    GOOGLE_API_KEY
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.google.gemini_live.llm import (
    GeminiLiveLLMService,
    GeminiModalities,
    InputParams,
)
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 Incoming call: {from_number} → {to_number}")
    print(f"🆔 Call ID: {call_id}")

    # Realtime multimodal model. Documentation:
    #   https://ai.google.dev/gemini-api/docs/multimodal-live
    gemini_live = GeminiLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/gemini-2.0-flash-exp",
        params=InputParams(
            modalities=GeminiModalities.AUDIO,
            temperature=0.7,
            system_instruction=(
                "You are a helpful and energetic voice assistant. "
                "Keep your responses concise and conversational."
            ),
        ),
    )

    voice_agent = VoiceAgent(
        instructions="You are a professional assistant.",
        greeting="Hi there! This is Gemini Live. How can I help you today?",
    )

    # No `stt`, no `tts` — Gemini Live owns audio in and audio out. Mode is
    # auto-detected from the absence of `tts`.
    await voice_agent.configure(
        llm=gemini_live,
        allow_interruptions=True,
    )

    print("🎙️  Agent ready and listening...")
    await voice_agent.start()
    print(f"🏁 Session ended: {call_id}")


async def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY is not set in .env")
        return

    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=True,
    )

    print("🚀 Gemini Live voice agent")
    print("   Waiting for incoming calls...")

    try:
        await agent.connect()
    except KeyboardInterrupt:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
