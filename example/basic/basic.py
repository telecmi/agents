"""
Basic Voice Agent Example - Complete Parameter Reference

This example demonstrates ALL available parameters and their usage.
Use this as a reference to understand what each parameter does.

Requirements:
    pip install "piopiy-ai[cartesia,deepgram,openai,silero]"

Environment Variables:
    AGENT_ID, AGENT_TOKEN
    OPENAI_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY
    AGENT_DEBUG (optional) - Set to "true" for verbose logging
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(
    agent_id: str,      # Your agent ID from Piopiy dashboard
    call_id: str,       # Unique identifier for this call
    from_number: str,   # Caller's phone number (E.164 format)
    to_number: str,     # Called phone number (E.164 format)
    metadata: dict = None,  # Optional custom data passed with the call
    **kwargs
):
    """
    This function is called for EVERY incoming call to your agent.
    
    Parameters explained:
    - agent_id: Your agent's unique ID (from dashboard)
    - call_id: Unique ID for this specific call session
    - from_number: Who is calling (e.g., "+14155551234")
    - to_number: Which number they called (e.g., "+14155556789")
    - metadata: Custom data you can pass when initiating calls
                Example: {"customer_id": "123", "language": "en"}
    """
    
    print(f"📞 New Call Session")
    print(f"   Call ID: {call_id}")
    print(f"   From: {from_number}")
    print(f"   To: {to_number}")
    print(f"   Extra Param: {metadata}")
    
    # Example: Use metadata to customize behavior
    customer_name = metadata.get("customer_name", "there") if metadata else "there"
    language = metadata.get("language", "en") if metadata else "en"
    
    # VoiceAgent Configuration - ALL parameters shown
    voice_agent = VoiceAgent(
        # REQUIRED: System instructions for the AI
        instructions=f"You are a helpful AI assistant. The customer's name is {customer_name}.",
        
        # REQUIRED: First thing the agent says when call connects
        greeting=f"Hello {customer_name}! How can I help you today?",
        
        # OPTIONAL: Initial conversation context
        # initial_messages=[
        #     {"role": "system", "content": "You are a sales assistant."},
        #     {"role": "user", "content": "I'm interested in your product."}
        # ],
        
        # OPTIONAL: End-of-turn configuration
        # end_of_turn_mode="auto",  # Options: "auto", "manual"
    )

    # Speech-to-Text (STT) Configuration - ALL parameters
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        
        # Model selection
        model="nova-2",  # Options: nova-2, nova, base, enhanced
        
        # Language configuration
        language=language,  # e.g., "en-US", "es-ES", "fr-FR"
        
        # Transcription features
        smart_format=True,      # Auto-format numbers, dates, etc.
        punctuate=True,         # Add punctuation
        interim_results=True,   # Stream partial results
        
        # Optional: Custom vocabulary
        # keywords=["Piopiy", "VoIP"],  # Boost specific words
    )

    # Large Language Model (LLM) Configuration - ALL parameters
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        
        # Model selection
        model="gpt-4o-mini",  # Options: gpt-4o, gpt-4o-mini, gpt-4-turbo
        
        # Response behavior
        temperature=0.7,      # 0-2: Higher = more creative (default: 0.7)
        max_tokens=150,       # Max response length (default: 150)
        top_p=0.9,           # Nucleus sampling (default: 0.9)
        
        # Optional: Function calling
        # tools=[{
        #     "type": "function",
        #     "function": {
        #         "name": "get_weather",
        #         "description": "Get weather for a location",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "location": {"type": "string"}
        #             }
        #         }
        #     }
        # }],
    )

    # Text-to-Speech (TTS) Configuration - ALL parameters
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        
        # Voice selection
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",  # British Lady
        # Other voices:
        # - "79a125e8-cd45-4c13-8a67-188112f4dd22" (British Man)
        # - "694f9389-aac1-45b6-b726-9d9369183238" (American Woman)
        
        # Model selection
        model="sonic-english",  # Ultra-low latency
        
        # Audio quality
        sample_rate=24000,  # Options: 8000, 16000, 24000, 44100
        
        # Optional: Voice customization
        # speed=1.0,  # Speech rate (0.5-2.0)
    )

    # Start the voice agent - ALL parameters
    await voice_agent.Action(
        stt=stt,                    # Speech-to-Text service
        llm=llm,                    # Language Model service
        tts=tts,                    # Text-to-Speech service
        vad=True,                   # Voice Activity Detection (recommended)
        allow_interruptions=True,   # Allow user to interrupt agent (default: True)
        
        # Optional: Custom VAD configuration
        # vad_params={
        #     "threshold": 0.5,      # Detection sensitivity (0-1)
        #     "prefix_padding_ms": 300,
        #     "silence_duration_ms": 500
        # },
    )
    
    # Start processing the call
    await voice_agent.start()


async def main():
    """
    Main entry point - connects to Piopiy and waits for calls.
    """
    
    # Agent Configuration - ALL parameters
    agent = Agent(
        # REQUIRED: Your agent credentials
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        
        # REQUIRED: Session creation callback
        create_session=create_session,
        
        # OPTIONAL: Debug mode
        debug=True,
        
        # OPTIONAL: Custom event handlers
        # on_call_started=lambda call_id: print(f"Call {call_id} started"),
        # on_call_ended=lambda call_id: print(f"Call {call_id} ended"),
    )
    
    print("🚀 Agent starting...")
    print(f"   Agent ID: {os.getenv('AGENT_ID')}")
    print(f"   Debug: {os.getenv('AGENT_DEBUG', 'false')}")
    print("   Waiting for calls...")
    
    # Connect and start listening for calls
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
