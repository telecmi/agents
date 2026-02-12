"""
Local Whisper STT Example

Faster-Whisper running locally (no API key needed).

Requirements:
    pip install "piopiy-ai[whisper,openai,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    OPENAI_API_KEY
    CARTESIA_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.whisper.stt import WhisperSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Local Whisper STT")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using local Whisper for speech recognition. How can I help you?",
    )

    # Local Whisper - runs on your machine
    stt = WhisperSTTService(
        model="base",  # Options: tiny, base, small, medium, large
        language="en"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"
    )

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    
    print("🚀 Local Whisper STT Example")
    print("   Model: base (runs locally)")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
