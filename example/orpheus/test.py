import asyncio
import os

#from piopiy.services.opensource.orpheus.tts import OrpheusTTS
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy


import dotenv


dotenv.load_dotenv()
async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are an advanced voice AI for cloud telephony sales assistant .you response only in english",
        greeting="Hello! How can I help you today?",
    )

    vad = SileroVADAnalyzer()
   
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    #tts = OrpheusTTS(base_url="ws://192.168.0.120:8765", sample_rate=24000)
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"), voice_id="bdab08ad-4137-4548-b9db-6142854c7525")

    #await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts,vad=vad,allow_interruptions=True,interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
    #await voice_agent.start()

    pipeline = Pipeline([
        transport.input(),
        stt,
        aggregators.user(),
        llm,
        tts,
        transport.output(),
        aggregators.assistant(),
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            interruption_strategies=[MinWordsInterruptionStrategy(min_words=1)],
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
