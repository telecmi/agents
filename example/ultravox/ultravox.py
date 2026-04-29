# Sales CRM voice agent example (audio-LLM hybrid: Ultravox in, external TTS out)
import asyncio
import os

from dotenv import load_dotenv
from piopiy.agent import Agent
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.transcriptions.language import Language
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.tts import DeepgramTTSService
from piopiy.services.opensource.ultravox.omni import UltravoxService  # audio-in LLM

load_dotenv()

async def create_session():
    voice_agent = VoiceAgent(
        instructions=(
            "You are an advanced voice AI sales assistant for a CRM platform. "
            "Your role is to engage with potential customers, understand their needs, "
            "and effectively communicate how our CRM solutions can address their challenges. "
            "Provide clear, concise, and persuasive information to help them make informed decisions. "
            "Always be courteous, professional, and ready to assist with any sales-related inquiries."
        ),
        greeting="Hello, good morning! I am Tara from Telecmi you had inquired at our website regarding the products is it a good time to talk to you?"
    )

    # --- OMNI (Ultravox) — single speech runtime (no separate STT/LLM) ---
    omni = UltravoxService(
        server_url="ws://0.0.0.0:8766",
        language=Language.EN,
        # system_prompt=(
        #     '''You are an advanced voice AI sales assistant for a CRM platform.Be proactive, clear, concise, and persuasive.
            
        #     This is the format in which you have to give the response in **JSON FORMAT**
        #     ** OUTPUT FORMAT **
        #     ```
        #     {
        #     "function_call":<Boolean>
        #     "response":"<YOUR RESPONSE>",
        #     "question":"<What has User Asked"
        #     }
        #     ```
        #     '''
            
        # ),
        temperature=0.7,
        max_tokens=200
        # add any tool/memory wiring your Ultravox omni supports
    )

    # --- TTS ---
    #tts = OrpheusTTS(base_url="ws://0.0.0.0:8765", sample_rate=24000)
    tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    # --- Optional VAD (recommended for telephony) ---
    vad = SileroVADAnalyzer()

    # Audio-LLM hybrid: Ultravox does ASR+LLM, external TTS speaks the reply.
    # Pipeline: Transport.input → llm (Ultravox) → tts → Transport.output
    await voice_agent.configure(
        llm=omni,           # Ultravox replaces both STT and the LLM stage
        tts=tts,            # external TTS for the agent's voice
        vad=vad,
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    )

    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    print(os.getenv("AGENT_ID"))
    asyncio.run(main())
