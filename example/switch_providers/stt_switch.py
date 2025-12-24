import asyncio
import os
import dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.speechmatics.stt import SpeechmaticsSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.pipeline.service_switcher import ServiceSwitcher, ServiceSwitcherStrategyManual
from piopiy.adapters.schemas.function_schema import FunctionSchema

dotenv.load_dotenv()

async def create_session(call_id: str, agent_id: str, from_number: str, to_number: str):
    # Initialize STT Services to switch between
    deepgram_stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    speechmatics_stt = SpeechmaticsSTTService(api_key=os.getenv("SPEECHMATICS_API_KEY"))

    # Create Service Switcher for STT
    stt_services = ServiceSwitcher(
        services=[deepgram_stt, speechmatics_stt],
        strategy_type=ServiceSwitcherStrategyManual
    )

    # Core Services
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"), 
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525"
    )

    # Define the switching tool handler
    async def switch_stt_handler(params):
        provider = params.arguments.get("provider")
        target_service = None
        if provider and provider.lower() == "deepgram":
            target_service = deepgram_stt
        elif provider and provider.lower() == "speechmatics":
            target_service = speechmatics_stt
        
        if target_service:
            print(f"Switching STT provider to {provider}")
            await voice_agent.switch_service(target_service)
            return f"Switched STT provider to {provider}"
        else:
            return f"Provider {provider} not found available options: deepgram, speechmatics"

    # Define Tool Schema
    switch_tool_schema = FunctionSchema(
        name="switchstt",
        description="Switch the current speech-to-text (STT) provider.",
        properties={
            "provider": {
                "type": "string",
                "description": "The name of the provider to switch to (e.g., 'deepgram', 'speechmatics')."
            }
        },
        required=["provider"]
    )

    # Initialize Voice Agent
    voice_agent = VoiceAgent(
        instructions="You are a helpful assistant. You can switch your hearing (STT) provider using the 'switchstt' tool. You start with Deepgram.",
        greeting="Hello! I can switch my hearing provider. Just ask me to switch to Speechmatics or Deepgram.",
    )

    # Register the tool
    voice_agent.add_tool(switch_tool_schema, switch_stt_handler)

    # Start Action with the Switcher
    await voice_agent.Action(
        stt_switcher=stt_services,
        llm=llm,
        tts=tts,
        vad=True,
        allow_interruptions=True
    )
    
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
