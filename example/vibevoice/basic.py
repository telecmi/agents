import asyncio
import os

from piopiy.agent import Agent
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.opensource.vibevoice.tts import OpenVibeVoiceTTSService
import dotenv

dotenv.load_dotenv()

async def create_session(call_id: str, agent_id: str, from_number: str, to_number: str):

    call_id = call_id
    agent_id = agent_id
    from_number = from_number
    to_number = to_number

    instruction ="You are a polite and professional conversation representative from Krishna Real Estate. Your role is to engage in natural, general conversation with clients."
    voice_agent = VoiceAgent(
        instructions=instruction,
        greeting="Hello, I am Alex from Krishna Real Estate. How can I assist you today?",
    )

   
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    
    tts = OpenVibeVoiceTTSService(
        server_url=os.getenv("VIBEVOICE_SERVER_URL"),
        sample_rate=24000,
    )

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True, allow_interruptions=True)
    await voice_agent.start()

async def main():
    print("Starting voice agent...")
    print(f"AGENT_IDA: {os.getenv('AGENT_IDA')}, AGENT_TOKENA: {os.getenv('AGENT_TOKENA')}")
    print(f"DEEPGRAM_API_KEY: {os.getenv('DEEPGRAM_API_KEY')}, OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}, TTS_SERVER_URL: {os.getenv('VIBEVOICE_SERVER_URL')}")
    agent = Agent(   
        agent_id=os.getenv("AGENT_IDA"),
        agent_token=os.getenv("AGENT_TOKENA"),
        create_session=create_session,
    )
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
