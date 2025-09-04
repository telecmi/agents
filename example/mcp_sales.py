import asyncio
import os

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService
import dotenv

from piopiy.services.mcp_service import MCPClient, StreamableHttpParameters

dotenv.load_dotenv()

async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are a sales voice AI agent. Your task is to sell the Voice AI agent product to the customer.",
        greeting="Hello! How can I help you today?",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"),
                             voice_id="bdab08ad-4137-4548-b9db-6142854c7525"
                             )
    
    
    mcp = MCPClient(
      StreamableHttpParameters(
        url="your mcp server url here",
        # headers={"Authorization": "Bearer <TOKEN>"}  # optional
    )
)
    mcp_tools=await mcp.register_tools(llm)

    await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts,mcp_tools=mcp_tools)
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
