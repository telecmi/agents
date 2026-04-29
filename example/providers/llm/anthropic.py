"""
Anthropic Claude LLM Example

High-quality reasoning with Claude 3.5 Sonnet.

Requirements:
    pip install "piopiy-ai[deepgram,anthropic,cartesia,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    DEEPGRAM_API_KEY
    ANTHROPIC_API_KEY - Get from https://console.anthropic.com/
    CARTESIA_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.anthropic.llm import AnthropicLLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Using Claude 3.5 Sonnet")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant powered by Claude.",
        greeting="Hello! I'm powered by Claude 3.5 Sonnet. How can I help you?",
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2"
    )

    # Anthropic Claude - Excellent reasoning
    llm = AnthropicLLMService(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",  # Latest Claude
        max_tokens=1024,
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
    
    print("🚀 Anthropic Claude Example")
    print("   Model: Claude 3.5 Sonnet")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
