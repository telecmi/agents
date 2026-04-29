import asyncio
import os
import dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent

from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.llm_service import FunctionCallParams

dotenv.load_dotenv()

# ---- 1. Tool handler function ----
async def get_current_weather(params: FunctionCallParams):
    args = getattr(params, "args", {}) or {}
    location = args.get("location", "Chennai")
    
    # Normally you would replace this with a real HTTP request to a Weather API
    print(f"🌦️ Tool Executing: Looking up weather for {location}")
    response_data = {"location": location, "temperature_c": 30}
    
    # Send the tool result back to the LLM to generate speech
    await params.result_callback(response_data)


# ---- 2. Tool schema definition ----
weather_function = FunctionSchema(
    name="get_current_weather",
    description="Get current weather for a location.",
    properties={
        "location": {
            "type": "string",
            "description": "City name to look up weather for.",
        }
    },
    required=["location"],
)


# ---- 3. Session factory ----
async def create_session(agent_id: str, call_id: str, from_number: str, to_number: str):
    print(f"📞 New Tool Calling Session: {call_id} from {from_number}")
    
    voice_agent = VoiceAgent(
        instructions="You are a helpful weather assistant. Use your tools to check the weather when asked.",
        greeting="Hello! Try asking me about the weather in Chicago or London.",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"), model="nova-2")
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525", # British Lady
    )

    # Register the tool!
    voice_agent.add_tool(weather_function, get_current_weather)

    await voice_agent.configure(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=True,
        allow_interruptions=True,
    )

    await voice_agent.start()


# ---- 4. Entrypoint ----
async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    
    print("🚀 Tool Calling Agent starting...")
    print("   Waiting for calls...")
    
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
