# Sales CRM voice agent example
import asyncio
from piopiy.agent import Agent
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.voice_agent import VoiceAgent
from dotenv import load_dotenv
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer

load_dotenv()
import os

async def create_session():
   
   voice_agent = VoiceAgent(
    instructions="You are a proactive sales assistant for a CRM platform. Help manage customer relationships and promote our offerings.",
    greeting="Hi there! Looking for a CRM solution? I'm here to help with sales questions.",
   )

   stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
   llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
   tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"), voice_id="bdab08ad-4137-4548-b9db-6142854c7525")
   vad = SileroVADAnalyzer()


   voice_agent.AgentAction(stt=stt, llm=llm, tts=tts, vad=vad, allow_interruptions=True, interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
   await voice_agent.start()


   

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

