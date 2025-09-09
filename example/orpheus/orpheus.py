# Sales CRM voice agent example
import asyncio
import os
from piopiy.agent import Agent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.voice_agent import VoiceAgent
from dotenv import load_dotenv
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopyi.services.opensource.orpheus import OrpheusTTSService

load_dotenv()

async def create_session():
    global tts
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
    tts = OrpheusTTSService(
            server_url="ws://SERVER_IP:60007",
            api_key="telecmi@123"
        )

    
    vad = SileroVADAnalyzer()


    await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts, vad=vad, allow_interruptions=True, interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
    await voice_agent.start()


   

async def main():
    agent = Agent(
        agent_id="AGENT_ID",
        agent_token="AGENT_TOKEN",
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    print(os.getenv("AGENT_ID"))
    asyncio.run(main())

