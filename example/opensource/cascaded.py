"""Fully open-source cascaded voice agent.

Stack:
    STT  : Whisper (faster-whisper, runs locally)
    LLM  : Ollama (local model server, e.g. Llama 3.1)
    TTS  : Chatterbox (self-hosted WebSocket server)

Pipeline:
    transport.input → whisper STT → ollama LLM → chatterbox TTS → transport.output

Requirements:
    pip install "piopiy-ai[whisper,silero]" python-dotenv

Runtimes you must start separately:
    1. Ollama:     https://ollama.ai          (then `ollama pull llama3.1`)
    2. Chatterbox: https://github.com/piopiy-ai/chatterbox-tts  (port 6078)

Environment:
    AGENT_ID, AGENT_TOKEN
    OLLAMA_BASE_URL    (default: http://localhost:11434)
    CHATTERBOX_BASE_URL (default: ws://localhost:6078)
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.ollama.llm import OLLamaLLMService
from piopiy.services.opensource.chatterbox.tts import ChatterboxTTSService
from piopiy.services.whisper.stt import WhisperSTTService
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 Open-source cascaded call {call_id}: {from_number} → {to_number}")

    voice_agent = VoiceAgent(
        instructions=(
            "You are a friendly local-first voice assistant. "
            "Keep responses under two sentences."
        ),
        greeting="Hi! Running fully on open-source models today. How can I help?",
    )

    # Whisper runs locally via faster-whisper. "small" is a good latency/quality
    # trade-off on CPU; bump to "medium" or "large-v3" if you have a GPU.
    stt = WhisperSTTService(model="small", language="en")

    # Ollama: any model you've pulled (`ollama pull <name>`) will work.
    llm = OLLamaLLMService(
        model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    # Chatterbox: self-hosted streaming TTS server.
    tts = ChatterboxTTSService(
        base_url=os.getenv("CHATTERBOX_BASE_URL", "ws://localhost:6078"),
        sample_rate=24000,
    )

    await voice_agent.configure(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )
    print("🚀 Open-source cascaded agent starting...")
    print("   STT: Whisper (local)")
    print("   LLM: Ollama (local)")
    print("   TTS: Chatterbox (local)")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
