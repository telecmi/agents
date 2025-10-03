import asyncio
import os


from piopiy.services.opensource.orpheus.tts import OrpheusTTS
from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService

import dotenv


dotenv.load_dotenv()
async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are an advanced voice AI for cloud telephony sales assistant.",
        greeting="Hello! How can I help you today?",
    )

    vad = {
       "confidence": 0.7,
        "start_secs": 0.2,
        "stop_secs": 0.8,
        "min_volume": 0.6    # passthrough
        }
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
   
    #tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"), voice_id="bdab08ad-4137-4548-b9db-6142854c7525")
    tts = OrpheusTTS(base_url="ws://0.0.0.0:8765", sample_rate=24000)

    await voice_agent.Action(stt=stt, llm=llm, tts=tts,vad=vad)
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
