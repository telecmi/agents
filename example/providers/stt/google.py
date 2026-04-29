"""
Google Cloud Speech STT Example

Google Cloud Speech-to-Text API.

Requirements:
    pip install "piopiy-ai[google,openai,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    GOOGLE_APPLICATION_CREDENTIALS - Path to credentials JSON
    OPENAI_API_KEY
    CARTESIA_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.google.stt import GoogleSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Google Cloud Speech STT")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using Google Cloud Speech. How can I help you?",
    )

    stt = GoogleSTTService(
        credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        language="en-US",
        model="latest_long"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
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
    
    print("🚀 Google Cloud Speech STT Example")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
