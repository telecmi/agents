import asyncio
import os
import dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy_voice import RestClient

dotenv.load_dotenv()

async def create_session(agent_id, call_id, from_number, to_number, **kwargs):
    print(f"📞 New Call Transfer Session: {call_id} from {from_number}")
    
    # Initialize the REST Client for triggering the transfer
    rest_client = RestClient(token=os.getenv("PIOPIY_TOKEN"))
    
    # 1. Initialize the Voice Agent
    voice_agent = VoiceAgent(
        instructions="""
            You are a helpful customer support agent. 
            If the customer asks for a human, a supervisor, or an expert, 
            use the 'transfer_to_human' tool to hand off the call.
        """,
        greeting="Hello! I am the Piopiy Support Bot. How can I help you today?",
    )

    # 2. Define the Transfer Tool Handler
    async def transfer_handler(params):
        target_number = os.getenv("TRANSFER_NUMBER", "+15550001234") 
        caller_id = os.getenv("PIOPIY_NUMBER", from_number) # Use the Piopiy number as caller_id
        
        print(f"🔄 Tool Triggered: Transferring call {call_id} to {target_number}...")
        
        try:
            # Official PCMO Pipeline structure as per .pvo_tmp documentation
            pipeline = [
                {
                    "action": "connect",
                    "params": {
                        "caller_id": caller_id
                    },
                    "endpoints": [
                        {
                            "type": "pstn",
                            "number": target_number
                        }
                    ]
                }
            ]
            
            # Use the REST Client to re-route the active call
            response = rest_client.voice.transfer(call_id, pipeline)
            print(f"✅ Transfer Response: {response}")
            
            return "Sure, I am transferring you to a human expert now. Please hold."
        except Exception as e:
            print(f"❌ Transfer Failed: {e}")
            return "I apologize, but I encountered an error while trying to transfer the call."

    # 3. Define the Tool Schema
    transfer_tool = FunctionSchema(
        name="transfer_to_human",
        description="Transfer the current call to a human support agent.",
        properties={}, # No arguments needed for this simple handoff
        required=[]
    )

    # 4. Standard Services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"), model="nova-2")
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"))

    # Register the Tool
    voice_agent.add_tool(transfer_tool, transfer_handler)

    # Start the Action
    await voice_agent.configure(
        stt=stt,
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
    
    print("🚀 Call Transfer Agent starting...")
    print("   Waiting for calls...")
    
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
