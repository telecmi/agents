"""
Deepgram TTS Example

Deepgram Aura text-to-speech.

Requirements:
    pip install "piopiy-ai[deepgram,openai,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY - Also used for TTS
    OPENAI_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.deepgram.tts import DeepgramTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Deepgram Aura TTS")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using Deepgram Aura for voice synthesis. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # Deepgram Aura TTS
    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        voice="aura-asteria-en",
        sample_rate=24000
    )

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    
    print("🚀 Deepgram Aura TTS Example")
    print("   Voice: Aura Asteria")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
