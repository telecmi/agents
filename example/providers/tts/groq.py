"""
Groq TTS Example

Groq Whisper-based text-to-speech.

Requirements:
    pip install "piopiy-ai[groq,deepgram,openai,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    OPENAI_API_KEY (for LLM)
    GROQ_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.groq.tts import GroqTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Groq TTS")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using Groq for voice synthesis. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # Groq TTS
    tts = GroqTTSService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="whisper-large-v3",
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
    
    print("🚀 Groq TTS Example")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
