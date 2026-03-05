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

async def create_session(agent_id, call_id, from_number, to_number, **kwargs):
    print(f"📞 New MCP Knowledge Session: {call_id} from {from_number}")
    
    voice_agent = VoiceAgent(
        instructions="You are a sales voice AI agent. Your task is to sell the Voice AI agent product to the customer.",
        greeting="Hello! I am the Piopiy Knowledge Agent. How can I help you today?",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"), model="nova-2")
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525"
    )
    
    # Initialize the MCP Client
    # This example connects to a hosted or local MCP server via HTTP/SSE
    mcp = MCPClient(
        StreamableHttpParameters(
            url="http://localhost:8000/sse", # Replace with your MCP server URL
        )
    )
    
    print("🔗 Registering MCP tools...")
    mcp_tools = await mcp.register_tools(llm)

    await voice_agent.Action(
        stt=stt, 
        llm=llm, 
        tts=tts,
        vad=True,
        mcp_tools=mcp_tools
    )
    
    await voice_agent.start()

async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    
    print("🚀 MCP Knowledge Agent starting...")
    print("   Waiting for calls...")
    
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
