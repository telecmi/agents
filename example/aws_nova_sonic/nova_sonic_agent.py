"""Speech-to-Speech voice agent using AWS Nova Sonic.

Amazon Nova Sonic is a bidirectional speech model. It consumes user audio
and emits agent audio — `configure(llm=...)` with no `tts` puts the agent
in speech-to-speech mode.

Requirements:
    pip install "piopiy-ai[aws-nova-sonic,silero]"   # Python 3.12+

Environment:
    AGENT_ID, AGENT_TOKEN
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_REGION  (default: us-east-1)
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.aws.nova_sonic.llm import AWSNovaSonicLLMService
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 Nova Sonic call {call_id}: {from_number} → {to_number}")

    voice_agent = VoiceAgent(
        instructions="You are a calm and helpful voice assistant.",
        greeting="Hi! This is Nova Sonic. How can I help you today?",
    )

    llm = AWSNovaSonicLLMService(
        access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region=os.getenv("AWS_REGION", "us-east-1"),
        model="amazon.nova-2-sonic-v1:0",
        voice_id="matthew",                 # see Nova voice docs for all options
        system_instruction="Respond conversationally; keep replies under 50 words.",
    )

    # Speech-to-speech: no stt, no tts.
    await voice_agent.configure(llm=llm, allow_interruptions=True)
    await voice_agent.start()


async def main():
    if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
        raise SystemExit("❌ AWS credentials not set")

    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )
    print("🚀 AWS Nova Sonic agent — waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
