import asyncio
import os

from piopiy.agent import Agent
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

import dotenv


dotenv.load_dotenv()

async def create_session(call_id: str, agent_id: str, from_number: str, to_number: str):

    call_id = call_id
    agent_id = agent_id
    from_number = from_number
    to_number = to_number

   
    voice_agent = VoiceAgent(
        instructions="You are an advanced voice AI.",
        greeting="Hello! How can I help you today?",
    )

   
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"), voice_id="bdab08ad-4137-4548-b9db-6142854c7525")

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True, allow_interruptions=True, interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
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
