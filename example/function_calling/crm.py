# CRM voice agent with function calling
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


# ---- Tool handlers ----
async def get_crm_pricing(params: FunctionCallParams):
    # Extract inputs the model sent
    args = getattr(params, "args", {}) or {}
    crm_type = args.get("crm_type", "generic")
    currency = args.get("currency", "USD")
    # Your logic here based on crm_type
    await params.result_callback({"crm_price": 100, "currency": currency, "crm_type": crm_type})


async def get_crm_features(params: FunctionCallParams):
    args = getattr(params, "args", {}) or {}
    crm_type = args.get("crm_type", "generic")
    # Your logic here based on crm_type
    await params.result_callback({"crm_features": ["Leads", "Pipelines", "Workflows"], "crm_type": crm_type})


# ---- Tool schemas (inputs only) ----
pricing_function = FunctionSchema(
    name="get_crm_pricing",
    description="Get current pricing for a CRM type.",
    properties={
        "crm_type": {
            "type": "string",
            "description": "The CRM type, e.g. Zoho, Salesforce.",
        },
        "currency": {
            "type": "string",
            "description": "The currency, e.g. USD, INR.",
        },
    },
    required=["crm_type", "currency"],
)

features_function = FunctionSchema(
    name="get_crm_features",
    description="List key features for a CRM type.",
    properties={
        "crm_type": {
            "type": "string",
            "description": "The CRM type, e.g. Zoho, Salesforce.",
        }
    },
    required=["crm_type"],
)


# ---- Session factory ----
async def create_session():
    voice_agent = VoiceAgent(
        instructions=(
            "You are an advanced voice AI sales assistant for a CRM platform. "
            "Understand the caller's needs and explain pricing & features clearly. "
            "Be concise, courteous, and helpful."
        ),
        greeting="Hello! Welcome to TeleCMI — how can I help you today?",
    )

    
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525",
    )

    # Pair schemas with handlers (advertise to model + bind runtime)
    voice_agent.add_tool(pricing_function, get_crm_pricing)
    voice_agent.add_tool(features_function, get_crm_features)


    vad = SileroVADAnalyzer()

    await voice_agent.AgentAction(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=vad,
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    )

    # Optional: seed a first user turn to nudge tool-calls in testing
    # voice_agent._messages.append({"role": "user", "content": "What's the price for Zoho CRM?"})

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
