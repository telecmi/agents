"""Basic Voice Agent — complete parameter reference (cascaded mode).

Shows every parameter `VoiceAgent` and `voice_agent.configure(...)` accept.
For a speech-to-speech example, see `example/gemini_live/gemini_live_agent.py`.

Requirements:
    pip install "piopiy-ai[cartesia,deepgram,openai,silero]"

Environment variables:
    AGENT_ID, AGENT_TOKEN
    OPENAI_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY
    AGENT_DEBUG (optional) — set to "true" for verbose logging
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(
    agent_id: str,
    call_id: str,
    from_number: str,
    to_number: str,
    metadata: dict = None,
    **kwargs,
):
    """Called for every incoming call."""
    print("📞 New call session")
    print(f"   Call ID:  {call_id}")
    print(f"   From:     {from_number}")
    print(f"   To:       {to_number}")
    print(f"   Metadata: {metadata}")

    customer_name = (metadata or {}).get("customer_name", "there")
    language = (metadata or {}).get("language", "en")

    voice_agent = VoiceAgent(
        # System prompt — controls the agent's behaviour and tone.
        instructions=f"You are a helpful AI assistant. The customer's name is {customer_name}.",
        # First thing the agent says when the call connects.
        greeting=f"Hello {customer_name}! How can I help you today?",
        # Cancel the call after this many seconds with no agent activity.
        idle_timeout_secs=60,
    )

    # Speech-to-Text
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        language=language,
        smart_format=True,
        punctuate=True,
        interim_results=True,
    )

    # Large Language Model
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=150,
        top_p=0.9,
    )

    # Text-to-Speech
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="f8f5f1b2-f02d-4d8e-a40d-fd850a487b3d",
        model="sonic-3",
        sample_rate=24000,
    )

    # Configure the pipeline. With stt + llm + tts → cascaded mode.
    # (Omit `tts=` to switch to speech-to-speech mode with a realtime model.)
    await voice_agent.configure(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=True,                  # True | False | dict | SileroVADAnalyzer
        allow_interruptions=True,
    )

    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )

    print("🚀 Agent starting...")
    print(f"   Agent ID: {os.getenv('AGENT_ID')}")
    print("   Waiting for calls...")

    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
