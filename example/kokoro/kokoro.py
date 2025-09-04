# Sales CRM voice agent example
import asyncio
import os

from dotenv import load_dotenv
from piopiy.agent import Agent
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.opensource.kokoro import KokoroTTSService
from piopiy.transcriptions.language import Language
from piopiy.voice_agent import VoiceAgent

load_dotenv()

async def create_session():
   
    voice_agent = VoiceAgent(
        instructions=(
            "You are an advanced voice AI sales assistant for a CRM platform "
            "Your role is to engage with potential customers understand their needs "
            "and effectively communicate how our CRM solutions can address their challenges "
            "Provide clear concise and persuasive information to help them make informed decisions "
            "Always be courteous professional and ready to assist with any sales related inquiries"
        ),
    
        greeting="Hello Good Morning Welcome to TeleCMI, how can I help you today?"
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))


    #KokoroTTS
    tts = KokoroTTSService(
        model_type = "normal", #or "int8-gpu" or "int8-cpu"
        voice_id = "af_sarah",
        is_phonemes = False,
        params=KokoroTTSService.InputParams(
            language=Language.EN,  
            speed=1.2,
        ),
    )
    
    vad = SileroVADAnalyzer()


    await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts, vad=vad, allow_interruptions=True, interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
    await voice_agent.start()


   

async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    print(os.getenv("AGENT_ID"))
    asyncio.run(main())

