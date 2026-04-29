"""
ElevenLabs TTS Example

Highest quality, most expressive text-to-speech.

Requirements:
    pip install "piopiy-ai[deepgram,openai,elevenlabs,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    OPENAI_API_KEY
    ELEVENLABS_API_KEY - Get from https://elevenlabs.io/
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using ElevenLabs TTS")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using ElevenLabs for high-quality voice. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # ElevenLabs TTS - Highest quality
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        model="eleven_turbo_v2_5",
        stability=0.5,
        similarity_boost=0.75
    )

    await voice_agent.configure(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    
    print("🚀 ElevenLabs TTS Example")
    print("   Voice: Rachel")
    print("   Quality: Premium ⭐")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
