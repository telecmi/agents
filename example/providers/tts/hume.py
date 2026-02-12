"""
Hume AI TTS Example

Hume AI empathic text-to-speech.

Requirements:
    pip install "piopiy-ai[hume,deepgram,openai,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    OPENAI_API_KEY
    HUME_API_KEY - Get from https://www.hume.ai/
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.hume.tts import HumeTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Hume AI TTS")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using Hume AI for empathic voice. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # Hume AI TTS - Empathic voice
    tts = HumeTTSService(
        api_key=os.getenv("HUME_API_KEY"),
        voice_id="default",
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
    
    print("🚀 Hume AI TTS Example")
    print("   Empathic Voice")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
