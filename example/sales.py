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

from piopiy.transports.services.telecmi import TelecmiParams, TelecmiTransport
from dotenv import load_dotenv

from piopiy.frames.frames import LLMFullResponseEndFrame, LLMFullResponseStartFrame, LLMTextFrame

from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.frames.frames import BotSpeakingFrame

from piopiy.audio.vad.silero import SileroVADAnalyzer
#from pipecat.services.speechmatics.stt import SpeechmaticsSTTService
from piopiy.transcriptions.language import Language
from piopiy.frames.frames import TextFrame

load_dotenv()
import os

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
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525", 
    )
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {
            "role": "system",
            "content": "You are a friendly Voice AI assistant. Respond naturally and keep your answers conversational. You are a sales assistant for a company that sells software to businesses. You are given a transcript of a conversation between a customer and a sales representative. You are to respond to the customer's question or comment based on the conversation history. You are to respond naturally and keep your answers conversational. You are to respond in the same language as the customer.",
        }
    ]
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    pipe = Pipeline([
        transport.input(),
        stt,                        # STT
        context_aggregator.user(),                 # add user msg to context
        llm,                        # LLM
        tts,                        # TTS
        transport.output(),         # bot media out
        context_aggregator.assistant()
    ])

    task = PipelineTask(
        pipe
        ,params=PipelineParams(
            enable_metrics=True,
                enable_usage_metrics=True,
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
        idle_timeout_secs=60,  #
        idle_timeout_frames=(BotSpeakingFrame,LLMFullResponseEndFrame),  # Only monitor bot speaking
        cancel_on_idle_timeout=True )
    )


    @transport.event_handler("on_first_participant_joined")
    async def greet(_, _pid):
        print("greeting")
        await asyncio.sleep(1)
        await task.queue_frame(
            TextFrame(
                "Hello there! How are you doing today? Would you like to talk about the weather?"
            )
        )
    @transport.event_handler("on_participant_disconnected")
    async def on_participant_disconnected(transport, client):
            print(f"Participant disconnected")
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

