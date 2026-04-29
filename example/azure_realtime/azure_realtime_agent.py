"""Speech-to-Speech voice agent using Azure OpenAI Realtime.

Same OpenAI Realtime model surface, deployed on Azure. Constructor extends
``OpenAIRealtimeLLMService`` and accepts the full Azure WebSocket endpoint
(including api-version and deployment).

Requirements:
    pip install "piopiy-ai[azure,silero]"

Environment:
    AGENT_ID, AGENT_TOKEN
    AZURE_OPENAI_API_KEY
    AZURE_OPENAI_REALTIME_URL
        e.g. wss://my-project.openai.azure.com/openai/realtime
             ?api-version=2025-04-01-preview&deployment=my-realtime-deployment
"""

import asyncio
import os

from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.azure.realtime.llm import AzureRealtimeLLMService
from piopiy.services.openai.realtime import events
from piopiy.voice_agent import VoiceAgent

load_dotenv()


async def create_session(call_id, from_number, to_number, metadata=None, **_):
    print(f"📞 Azure Realtime call {call_id}: {from_number} → {to_number}")

    voice_agent = VoiceAgent(
        instructions="You are a friendly voice assistant. Keep replies concise.",
        greeting="Hi! This is Azure OpenAI Realtime. How can I help?",
    )

    llm = AzureRealtimeLLMService(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        base_url=os.environ["AZURE_OPENAI_REALTIME_URL"],
        session_properties=events.SessionProperties(
            voice="alloy",
            temperature=0.7,
        ),
    )

    # Speech-to-speech: no stt, no tts.
    await voice_agent.configure(llm=llm, allow_interruptions=True)
    await voice_agent.start()


async def main():
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        raise SystemExit("❌ AZURE_OPENAI_API_KEY is not set")
    if not os.getenv("AZURE_OPENAI_REALTIME_URL"):
        raise SystemExit("❌ AZURE_OPENAI_REALTIME_URL is not set")

    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "false").lower() == "true",
    )
    print("🚀 Azure Realtime agent — waiting for calls...")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
