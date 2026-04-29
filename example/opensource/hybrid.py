"""Open-source audio-LLM hybrid voice agent.

Ultravox is an audio-in / text-out LLM (it does ASR internally and reasons over
the audio in one model). It replaces both the STT and the text LLM stages of a
cascaded pipeline. We pair it with VibeVoice for high-quality TTS output.

Stack:
    Audio-LLM : Ultravox       (self-hosted WebSocket server)
    TTS       : VibeVoice      (self-hosted WebSocket server)

Pipeline:
    transport.input → ultravox (audio→text) → vibevoice TTS → transport.output

This is **audio-LLM hybrid mode** — `voice_agent.configure(llm=..., tts=...)`
without an `stt=` argument. Mode is auto-detected.

Requirements:
    pip install piopiy-ai python-dotenv

Runtimes you must start separately:
    1. Ultravox:  your self-hosted Ultravox server (default port 8766)
    2. VibeVoice: your self-hosted VibeVoice server (default port 8765)

Environment:
    AGENT_ID, AGENT_TOKEN
    ULTRAVOX_SERVER_URL  (default: ws://localhost:8766)
    VIBEVOICE_SERVER_URL (default: ws://localhost:8765)
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.audio.interruptions.min_words_interruption_strategy import (
    MinWordsInterruptionStrategy,
)
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.services.opensource.ultravox.omni import UltravoxService
from piopiy.transcriptions.language import Language
from piopiy.voice_agent import VoiceAgent

# VibeVoice path matches the existing example/ultravox/basic.py:
from piopiy.opensource.vibevoice.tts import OpenVibeVoiceTTSService

load_dotenv()


async def create_session(call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 Open-source hybrid call {call_id}: {from_number} → {to_number}")

    voice_agent = VoiceAgent(
        instructions=(
            "You are a polite and helpful customer support representative. "
            "Keep every response under 50 words."
        ),
        greeting="Hello! I'm Alice. How can I help you today?",
    )

    # Audio-in LLM: takes audio, emits text directly.
    llm = UltravoxService(
        server_url=os.getenv("ULTRAVOX_SERVER_URL", "ws://localhost:8766"),
        language=Language.EN,
        temperature=0.7,
        max_tokens=200,
    )

    # External TTS to speak the agent's replies.
    tts = OpenVibeVoiceTTSService(
        server_url=os.getenv("VIBEVOICE_SERVER_URL", "ws://localhost:8765"),
        sample_rate=24000,
    )

    # No `stt=` → audio-LLM hybrid pipeline:
    #   transport.input → llm (Ultravox) → tts (VibeVoice) → transport.output
    await voice_agent.configure(
        llm=llm,
        tts=tts,
        vad=SileroVADAnalyzer(),
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    )

    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )
    print("🚀 Open-source hybrid agent starting...")
    print("   Audio-LLM: Ultravox (local)")
    print("   TTS:       VibeVoice (local)")
    print("   Waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
