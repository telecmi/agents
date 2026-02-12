"""
Groq LLM Example

Ultra-fast inference with Llama 3.3 70B.
Recommended for low-latency applications.

Requirements:
    pip install "piopiy-ai[deepgram,groq,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    GROQ_API_KEY - Get from https://console.groq.com/
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
    print(f"📞 Call {call_id} - Using Groq (Ultra-Fast)")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm powered by Groq for ultra-fast responses. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    # Groq - Ultra-fast inference
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",  # Fast and capable
        temperature=0.7
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
    
    print("🚀 Groq LLM Example")
    print("   Model: Llama 3.3 70B")
    print("   Speed: Ultra-Fast ⚡")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
