"""
Piopiy AI Agent with Murf.ai TTS Example

This example demonstrates how to use Murf.ai TTS with Piopiy AI.
Murf.ai provides high-quality, natural-sounding voices with extensive customization options.

Requirements:
    pip install piopiy-ai[deepgram,openai,silero]
    pip install piopiy-murf-tts

Environment Variables:
    AGENT_ID - Your Piopiy agent ID
    AGENT_TOKEN - Your Piopiy agent token
    MURF_API_KEY - Your Murf.ai API key (get from https://murf.ai/api/dashboard)
    DEEPGRAM_API_KEY - Your Deepgram API key
    OPENAI_API_KEY - Your OpenAI API key
    AGENT_DEBUG - Set to "true" for verbose logging (optional)
"""

import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService

# Import Murf TTS from the external package
from piopiy_murf_tts import MurfTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    """
    Create a voice agent session with Murf.ai TTS.
    
    This function is called for each incoming call.
    """
    print(f"📞 Incoming call {call_id}")
    print(f"   From: {from_number}")
    print(f"   To: {to_number}")
    
    if metadata:
        print(f"   Metadata: {metadata}")

    # Create the voice agent
    voice_agent = VoiceAgent(
        instructions="""You are a helpful AI assistant with a natural, conversational voice.
        Be friendly, concise, and engaging in your responses.""",
        greeting="Hello! I'm your AI assistant powered by Murf AI. How can I help you today?",
    )

    # Configure Speech-to-Text (Deepgram)
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        language="en-US"
    )

    # Configure Large Language Model (OpenAI)
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # Configure Text-to-Speech (Murf.ai)
    tts = MurfTTSService(
        api_key=os.getenv("MURF_API_KEY"),
        params=MurfTTSService.InputParams(
            # Voice selection - see https://murf.ai/api/dashboard for all voices
            voice_id="en-UK-ruby",  # British English, female
            
            # Voice style
            style="Conversational",  # Options: "Conversational", "Narration", etc.
            
            # Speech rate adjustment (-50 to 50)
            rate=0,  # 0 = normal speed, positive = faster, negative = slower
            
            # Pitch adjustment (-50 to 50)
            pitch=0,  # 0 = normal pitch, positive = higher, negative = lower
            
            # Variation in pause, pitch, and speed (0-5, Gen2 only)
            variation=1,
            
            # Model selection
            model="FALCON",  # Options: "FALCON", "GEN2"
            
            # Audio quality
            sample_rate=44100,  # Options: 8000, 16000, 24000, 44100, 48000
            channel_type="MONO",  # Options: "MONO", "STEREO"
            format="PCM",  # Options: "MP3", "WAV", "FLAC", "ALAW", "ULAW", "PCM", "OGG"
            
            # Optional: Language for Gen2 model
            # multi_native_locale="en-US",
            
            # Optional: Custom pronunciation dictionary
            # pronunciation_dictionary={
            #     "Piopiy": {"pronunciation": "pie-oh-pie"},
            # },
        ),
    )

    # Start the agent with all services
    await voice_agent.Action(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=True,  # Enable voice activity detection
        allow_interruptions=True  # Allow user to interrupt the agent
    )
    
    await voice_agent.start()


async def main():
    """
    Initialize and start the Piopiy agent.
    """
    # Check for required environment variables
    required_vars = ["AGENT_ID", "AGENT_TOKEN", "MURF_API_KEY", "DEEPGRAM_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set them in your .env file:")
        print("AGENT_ID=your_agent_id")
        print("AGENT_TOKEN=your_agent_token")
        print("MURF_API_KEY=your_murf_api_key")
        print("DEEPGRAM_API_KEY=your_deepgram_key")
        print("OPENAI_API_KEY=your_openai_key")
        return

    # Create the agent
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=os.getenv("AGENT_DEBUG", "").lower() == "true"
    )
    
    print("🚀 Piopiy Agent with Murf.ai TTS starting...")
    print("   Voice: en-UK-ruby (British English, female)")
    print("   Style: Conversational")
    print("   Waiting for calls...")
    
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
