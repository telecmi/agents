# Weather info voice agent with function calling
import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent

from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy

from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.llm_service import FunctionCallParams

load_dotenv()


# ---- Tool handler ----
async def get_current_weather(params: FunctionCallParams):
    args = getattr(params, "args", {}) or {}
    location = args.get("location", "Chennai")
    # Replace with real API integration
    await params.result_callback({"location": location, "temperature_c": 30})


# ---- Tool schema ----
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


# ---- Session factory ----
async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are a helpful weather assistant.",
        greeting="Hello! Ask me about the weather.",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525",
    )

    voice_agent.add_tool(weather_function, get_current_weather)

    vad = SileroVADAnalyzer()
    await voice_agent.AgentAction(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=vad,
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    )

    await voice_agent.start()


# ---- Entrypoint ----
async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    await agent.connect()


if __name__ == "__main__":
    print("AGENT_ID:", os.getenv("AGENT_ID"))
    asyncio.run(main())
