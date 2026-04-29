import asyncio
import os
import dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

dotenv.load_dotenv()

async def create_session(agent_id: str, call_id: str, from_number: str, to_number: str, **kwargs):
    # Retrieve dynamic data passed from the outbound RestClient.ai.call()
    metadata = kwargs.get("metadata", {})
    customer_name = metadata.get("customer_name", "there")
    
    print(f"📞 New Phone Agent Session: {call_id} from {from_number}")
    if customer_name != "there":
        print(f"   Context: Outbound call to {customer_name}")
    
    # 1. VoiceAssistant Configuration
    voice_agent = VoiceAgent(
        instructions=f"""
            You are a helpful outbound sales representative.
            Your name is 'Piopiy Agent'.
            You are speaking to {customer_name}.
            Keep your responses extremely short and conversational.
        """,
        greeting=f"Hello {customer_name}! This is the Piopiy Phone Agent calling. Do you have a quick minute?",
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
        voice_id="694f9ed8-38bb-4e94-91ce-f831ae3f3fc0", # Delivery Man Voice
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
    
    print("🚀 Phone Agent starting...")
    print("   Waiting for outbound triggers...")
    
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
