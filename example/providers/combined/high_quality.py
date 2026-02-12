"""
Premium Quality Stack

Optimized for highest quality:
- AssemblyAI (STT)
- Claude 3.5 Sonnet (LLM)
- ElevenLabs (TTS)

Requirements:
    pip install "piopiy-ai[assemblyai,anthropic,elevenlabs,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    ASSEMBLYAI_API_KEY
    ANTHROPIC_API_KEY
    ELEVENLABS_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.assemblyai.stt import AssemblyAISTTService
from piopiy.services.anthropic.llm import AnthropicLLMService
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Premium Quality Stack ⭐")
    
    voice_agent = VoiceAgent(
        instructions="""You are a premium AI assistant. Provide thoughtful, 
        detailed responses with excellent reasoning.""",
        greeting="Hello! I'm your premium AI assistant. How may I help you today?",
    )

    # High-accuracy STT
    stt = AssemblyAISTTService(
        api_key=os.getenv("ASSEMBLYAI_API_KEY"),
        sample_rate=16000
    )

    # Best reasoning LLM
    llm = AnthropicLLMService(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.7
    )

    # Highest quality TTS
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model="eleven_turbo_v2_5",
        stability=0.5,
        similarity_boost=0.75
    )

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    
    print("🚀 Premium Quality Stack")
    print("   STT: AssemblyAI")
    print("   LLM: Claude 3.5 Sonnet")
    print("   TTS: ElevenLabs")
    print("   ⭐ Optimized for quality!")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
