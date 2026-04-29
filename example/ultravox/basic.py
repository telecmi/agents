import asyncio
import os

from dotenv import load_dotenv
from piopiy.agent import Agent
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.transcriptions.language import Language
from piopiy.voice_agent import VoiceAgent
from piopiy.opensource.ultravox.llm import OpenUltravoxLLM
from piopiy.opensource.vibevoice.tts import OpenVibeVoiceTTSService
from piopiy.transcriptions.language import Language


load_dotenv()

async def create_session(call_id: str, agent_id: str, from_number: str, to_number: str):
    call_id = call_id
    agent_id = agent_id
    from_number = from_number
    to_number = to_number
    instructions= "You are a polite and helpful customer support representative for a real estate company. Every response under 50 words."
    voice_agent = VoiceAgent(
        instructions=instructions,
        greeting="Hello! I'm Alice. A real estate agent. How can I assist you today?",
    )

    SERVER_URI = os.getenv("UX_SERVER_URL")
    print(f"Connecting to Ultravox server at {SERVER_URI}...")
    print(f"call_id: {call_id}, agent_id: {agent_id}, from_number: {from_number}, to_number: {to_number}")
    llm = OpenUltravoxLLM(
            server_url=SERVER_URI,
            caller_id=call_id,
            system_prompt=instructions,
        )
    
    tts = OpenVibeVoiceTTSService(
        server_url=os.getenv("VIBEVOICE_SERVER_URL"),
        sample_rate=24000,
    )

    vad = SileroVADAnalyzer()

    # Audio-LLM hybrid: Ultravox in, VibeVoice TTS out.
    await voice_agent.configure(
        llm=llm,
        tts=tts,
        vad=vad,
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    )

    await voice_agent.start()


async def main():

    agent = Agent(
        agent_id=os.getenv("AGENT_IDA"),
        agent_token=os.getenv("AGENT_TOKENA"),
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
