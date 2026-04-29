"""
Ollama LLM Example

Ollama for running local open-source models.

Requirements:
    pip install "piopiy-ai[ollama,deepgram,cartesia,silero]"
    
    Install Ollama: https://ollama.ai/
    Pull a model: ollama pull llama3.1

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    CARTESIA_API_KEY
    OLLAMA_BASE_URL (optional, default: http://localhost:11434)
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.ollama.llm import OllamaLLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Ollama (Local)")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm running locally with Ollama. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    # Ollama LLM - runs locally
    llm = OllamaLLMService(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model="llama3.1",  # Must be pulled first: ollama pull llama3.1
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
    
    print("🚀 Ollama LLM Example")
    print("   Model: Llama 3.1 (Local)")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
