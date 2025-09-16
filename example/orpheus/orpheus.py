import asyncio
import os

from piopiy.services.opensource.orpheus.tts import OrpheusTTS
from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from pipecat.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy


import dotenv


dotenv.load_dotenv()
async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are an advanced voice AI for cloud telephony .you response only in english and you can add <hmm..> tag when it require for natural voice",
        greeting="Hello! How can I help you today?",
    )

    vad = SileroVADAnalyzer()
   
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = OrpheusTTS(base_url="ws://192.168.0.120:8765", sample_rate=24000)

    await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts,vad=vad,allow_interruptions=True,interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
