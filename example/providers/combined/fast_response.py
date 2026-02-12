"""
Ultra-Low Latency Stack

Optimized for fastest possible response time:
- Deepgram Nova-2 (STT)
- Groq Llama 3.3 70B (LLM)
- Cartesia Sonic (TTS)

Requirements:
    pip install "piopiy-ai[deepgram,groq,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    GROQ_API_KEY
    CARTESIA_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.groq.llm import GroqLLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Ultra-Low Latency Stack ⚡")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant. Keep responses concise for fastest interaction.",
        greeting="Hello! I'm optimized for speed. How can I help you?",
    )

    # Fastest STT
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        interim_results=True
    )

    # Fastest LLM
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0.7
    )

    # Fastest TTS
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",
        model="sonic-english"
    )

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True, allow_interruptions=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    
    print("🚀 Ultra-Low Latency Stack")
    print("   STT: Deepgram Nova-2")
    print("   LLM: Groq Llama 3.3 70B")
    print("   TTS: Cartesia Sonic")
    print("   ⚡ Optimized for speed!")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
