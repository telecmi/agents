# user_bot.py

import asyncio
from piopiy import pipeline
from piopiy.agent import Agent, current_room, current_token
from piopiy.pipeline.runner import PipelineRunner
from piopiy.pipeline.task import PipelineParams, PipelineTask
from piopiy.processors.aggregators.openai_llm_context import OpenAILLMContext
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.transports.services.telecmi import TeleCMITransport, TeleCMIParams
from dotenv import load_dotenv
load_dotenv()
import os


# ... other imports

async def create_session():
    
    


    transport = TeleCMITransport(
        params=TeleCMIParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        )
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {
            "role": "system",
            "content": "You are a friendly AI assistant. Respond naturally and keep your answers conversational.",
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    task = PipelineTask(
        [
            transport.input(),  # Transport user input
            stt,
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        # Kick off the conversation.
        messages.append({"role": "system", "content": "Say hello and briefly introduce yourself."})
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)

async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    await agent.start()

if __name__ == "__main__":
    print(os.getenv("AGENT_ID"))
    asyncio.run(main())

