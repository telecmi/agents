import asyncio
import os
import dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService
from piopiy.pipeline.service_switcher import ServiceSwitcher, ServiceSwitcherStrategyManual
from piopiy.pipeline.llm_switcher import LLMSwitcher
from piopiy.adapters.schemas.function_schema import FunctionSchema

dotenv.load_dotenv()

async def create_session(call_id: str, agent_id: str, from_number: str, to_number: str):
    # Initialize Core Services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
   
    # Initialize TTS Services to switch between
    cartesia_tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"), 
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525" # Example Voice ID
    )
    
    elevenlabs_tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM" # Example Voice ID (Rachel)
    )

    # Create Service Switcher for TTS
    tts_services = ServiceSwitcher(
        services=[cartesia_tts, elevenlabs_tts],
        strategy_type=ServiceSwitcherStrategyManual
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    # Define the switching tool handler
    async def switch_provider_handler(params):
        provider = params.arguments.get("provider")
        target_service = None
        if provider and provider.lower() == "cartesia":
            target_service = cartesia_tts
        elif provider and provider.lower() == "elevenlabs":
            target_service = elevenlabs_tts
        
        if target_service:
            print(f"Switching TTS provider to {provider}")
            await voice_agent.switch_service(target_service)
            return f"Switched TTS provider to {provider}"
        else:
            return f"Provider {provider} not found available options: cartesia, elevenlabs"

    # Define Tool Schema
    switch_tool_schema = FunctionSchema(
        name="manualswitch",
        description="Switch the current TTS provider to a different one.",
        properties={
            "provider": {
                "type": "string",
                "description": "The name of the provider to switch to (e.g., 'cartesia', 'elevenlabs')."
            }
        },
        required=["provider"]
    )

    # Initialize Voice Agent
    voice_agent = VoiceAgent(
        instructions="You are a helpful assistant. You can switch your voice provider using the 'manualswitch' tool. You start with Cartesia.",
        greeting="Hello! I can switch my voice provider. Just ask me to switch to ElevenLabs or Cartesia.",
    )

    # Register the tool
    voice_agent.add_tool(switch_tool_schema, switch_provider_handler)

    # Start Action with the Switcher
    await voice_agent.Action(
        stt=stt,
        llm=llm,
        tts_switcher=tts_services,
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
