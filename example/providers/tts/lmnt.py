"""
LMNT TTS Example

LMNT ultra-low latency text-to-speech.

Requirements:
    pip install "piopiy-ai[lmnt,deepgram,openai,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    OPENAI_API_KEY
    LMNT_API_KEY - Get from https://www.lmnt.com/
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.lmnt.tts import LMNTTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using LMNT TTS")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! I'm using LMNT for ultra-low latency voice. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # LMNT TTS - Ultra-low latency
    tts = LMNTTTSService(
        api_key=os.getenv("LMNT_API_KEY"),
        voice_id="lily",
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
    
    print("🚀 LMNT TTS Example")
    print("   Voice: Lily")
    print("   Latency: Ultra-Low ⚡")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
