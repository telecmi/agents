"""
Mistral AI LLM Example

Mistral AI models for language understanding.

Requirements:
    pip install "piopiy-ai[mistral,deepgram,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    MISTRAL_API_KEY - Get from https://console.mistral.ai/
    CARTESIA_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.mistral.llm import MistralLLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Mistral AI")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant powered by Mistral.",
        greeting="Hello! I'm powered by Mistral AI. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    # Mistral LLM
    llm = MistralLLMService(
        api_key=os.getenv("MISTRAL_API_KEY"),
        model="mistral-large-latest",
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
    
    print("🚀 Mistral AI LLM Example")
    print("   Model: Mistral Large")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
