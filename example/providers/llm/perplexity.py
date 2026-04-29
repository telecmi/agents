"""
Perplexity LLM Example

Perplexity AI for search-augmented responses.

Requirements:
    pip install "piopiy-ai[perplexity,deepgram,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    PERPLEXITY_API_KEY - Get from https://www.perplexity.ai/
    CARTESIA_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.perplexity.llm import PerplexityLLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Perplexity AI")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant with search capabilities.",
        greeting="Hello! I'm powered by Perplexity AI with real-time search. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    # Perplexity LLM - search-augmented
    llm = PerplexityLLMService(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        model="llama-3.1-sonar-large-128k-online",
        temperature=0.7
    )

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"
    )

    await voice_agent.configure(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    
    print("🚀 Perplexity LLM Example")
    print("   Model: Sonar Large (Online)")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
