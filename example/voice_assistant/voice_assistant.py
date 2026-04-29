import asyncio
import os
import dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

dotenv.load_dotenv()

async def create_session(agent_id: str, call_id: str, from_number: str, to_number: str):
    print(f"📞 New Voice Assistant Session: {call_id} from {from_number}")
    
    # 1. VoiceAssistant Configuration
    voice_agent = VoiceAgent(
        instructions="""
            You are a helpful, extremely concise, and witty AI Voice Assistant.
            Keep all answers to one or two sentences maximum. 
            Your name is 'Piopiy Assistant'.
        """,
        greeting="Hello! I am your Piopiy Assistant. What can I do for you today?",
    )

    # 2. Speech-to-Text Setup
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2", 
        language="en-US"
    )

    # 3. LLM Setup
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
    )

    # 4. Text-to-Speech Setup
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",  # British Lady
    )

    # 5. Start the pipeline
    await voice_agent.configure(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=True,
        allow_interruptions=True,
    )
    
    await voice_agent.start()

async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    
    print("🚀 Voice Assistant starting...")
    print("   Waiting for calls...")
    
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
