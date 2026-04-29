"""
Google Gemini Live (Speech-to-Speech) Example

This example demonstrates how to use Google's Gemini Live API for
ultra-low latency, real-time Speech-to-Speech (S2S) conversations.

Since Gemini Live processes audio natively and responds with audio natively,
we bypass traditional STT and TTS services and construct a raw pipeline.

Requirements:
    pip install "piopiy-ai[google]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    GOOGLE_API_KEY - Get from https://aistudio.google.com/
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.transports.services.telecmi import TelecmiParams, TelecmiTransport
from piopiy.services.google.gemini_live.llm import GeminiLiveLLMService
from piopiy.pipeline.pipeline import Pipeline
from piopiy.pipeline.task import PipelineTask, PipelineParams
from piopiy.pipeline.runner import PipelineRunner
from piopiy.processors.aggregators.llm_context import LLMContext
from piopiy.processors.aggregators.llm_response_universal import LLMContextAggregatorPair, LLMUserAggregatorParams

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"📞 Call {call_id} - Gemini Live S2S Stack ⚡")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY is not set in .env")
        return
    print("✅ GOOGLE_API_KEY loaded")

    # Configure the WebRTC / WebSocket Transport for the call
    transport = TelecmiTransport(params=TelecmiParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_out_sample_rate=24000,
        audio_in_sample_rate=16000,
    ))

    # System instruction tells Gemini how to behave.
    # Pass it directly to GeminiLiveLLMService — this is the correct way for the Live API.
    instructions = (
        "You are a helpful and concise AI assistant powered by Google Gemini Live. "
        "When the call starts, greet the caller warmly and ask how you can help them."
    )

    # Configure Gemini Live Service (S2S)
    llm = GeminiLiveLLMService(
        api_key=api_key,
        voice_id="Charon",  # Voice selection for Gemini Live
        system_instruction=instructions,
    )

    # Initialize Context with a greeting trigger message.
    # Gemini Live needs a user turn in the history to generate its FIRST audio response.
    # Without this, the model sits silently waiting for the caller to speak first.
    ctx = LLMContext([
        {"role": "user", "content": "Hello"},
    ])

    # Create the context aggregators using the universal pair
    user_params = LLMUserAggregatorParams()
    context_aggregator = LLMContextAggregatorPair(context=ctx, user_params=user_params)

    # Build the Pipeline
    # Since Gemini Live is S2S, it consumes raw audio and produces raw audio.
    # No STT or TTS processors are needed!
    pipeline = Pipeline([
        transport.input(),
        context_aggregator.user(),
        llm,
        transport.output(),
        context_aggregator.assistant(),
    ])

    # Create the task and runner
    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))
    runner = PipelineRunner()

    # Log when the caller actually joins the room
    @transport.event_handler("on_first_participant_joined")
    async def _joined(transport, participant_id):
        print(f"📱 Caller joined (participant: {participant_id}) — Gemini will now speak.")

    # Gracefully handle disconnects
    @transport.event_handler("on_participant_disconnected")
    async def _left(_, __):
        print("Participant disconnected. Ending call.")
        await task.cancel()

    print("🚀 Gemini Live Pipeline started! Speak to your agent now.")

    # Run the pipeline
    await runner.run(task)


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )

    print("🚀 Google Gemini Live Agent Example")
    print("   Model: Gemini 2.5 Flash Native Audio")
    print("   Waiting for calls...")

    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
