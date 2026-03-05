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
from piopiy.adapters.schemas.function_schema import FunctionSchema

dotenv.load_dotenv()

async def create_session(agent_id: str, call_id: str, from_number: str, to_number: str):
    print(f"📞 New TTS Switch Session: {call_id} from {from_number}")
    
    # 1. Initialize Core Services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
   
    # 2. Initialize TWO different Text-to-Speech services
    cartesia_tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"), 
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525" 
    )
    
    elevenlabs_tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM" # Rachel
    )

    # 3. Create a Service Switcher container
    tts_services = ServiceSwitcher(
        services=[cartesia_tts, elevenlabs_tts],
        strategy_type=ServiceSwitcherStrategyManual
    )

    # 4. Initialize the Agent
    voice_agent = VoiceAgent(
        instructions="You are a helpful assistant. You start with Cartesia. If the user asks you to change your voice, use the 'manualswitch' tool.",
        greeting="Hello! I currently sound like Cartesia. Ask me to switch my voice to ElevenLabs!",
    )

    # 5. Define the tool that performs the switch
    async def switch_provider_handler(params):
        provider = params.arguments.get("provider")
        target_service = None
        
        if provider and provider.lower() == "cartesia":
            target_service = cartesia_tts
        elif provider and provider.lower() == "elevenlabs":
            target_service = elevenlabs_tts
        
        if target_service:
            print(f"🔄 Switching TTS provider to {provider}")
            await voice_agent.switch_service(target_service)
            return f"Successfully switched my voice to {provider}"
        else:
            return f"Provider {provider} not found. Available: cartesia, elevenlabs"

    switch_tool_schema = FunctionSchema(
        name="manualswitch",
        description="Switch the current TTS provider to a different one.",
        properties={
            "provider": {
                "type": "string",
                "description": "Provider to switch to ('cartesia' or 'elevenlabs')"
            }
        },
        required=["provider"]
    )

    # 6. Register Tool and Start Action
    voice_agent.add_tool(switch_tool_schema, switch_provider_handler)

    await voice_agent.Action(
        stt=stt,
        llm=llm,
        tts_switcher=tts_services, # Pass the switcher instead of a single TTS
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
    
    print("🚀 Switch Providers Agent starting...")
    print("   Waiting for calls...")
    
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
