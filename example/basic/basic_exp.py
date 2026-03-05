import asyncio
import os

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.groq.llm import GroqLLMService
from piopiy.services.cartesia.tts import CartesiaTTSService


async def create_session(agent_id, call_id, from_number, to_number, metadata=None, **kwargs):
    print(f"Incoming call {call_id} from {from_number} to {to_number}")
    if metadata:
        print(f"Call Extra Param: {metadata}")

    voice_agent = VoiceAgent(
        instructions=(
            "You are Tele CMI’s sales voice assistant. Your job is to deliver a short sales pitch, qualify the caller, "
            "and guide them to the next step (free trial or demo).\n"
            "Start immediately with a friendly pitch, then ask ONE question at a time.\n\n"

            "PITCH (say this first, in 1–2 sentences):\n"
            "Tele CMI helps businesses manage calls with products like Business Phone System, Cloud PBX, and a Cloud Contact Center. "
            "We also offer AI features like AI Agent Assist, Sentiment Analysis, and a platform to build conversational voice agents.\n\n"

            "QUALIFY (ask in this order):\n"
            "1) 'Which are you looking for today: Business Phone System, Cloud PBX, Contact Center, or an AI voice agent?'\n"
            "2) 'How many users or agents will use it, and is it mainly inbound or outbound calls?'\n"
            "3) 'Do you need CRM integration or developer API and webhooks?'\n\n"

            "RESPOND:\n"
            "- Recommend the best-fit product in ONE sentence using only relevant features.\n"
            "- Keep each reply 1–2 sentences.\n\n"

            "CLOSE:\n"
            "Ask: 'Would you like to start a free trial now, or book a quick demo?'"
        ),
        greeting="Welcome to Tele CMI! How can I help you today?",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = GroqLLMService(api_key=os.getenv("GROQ_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525"
    )

    await voice_agent.Action(stt=stt, llm=llm, tts=tts)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=True
    )
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())