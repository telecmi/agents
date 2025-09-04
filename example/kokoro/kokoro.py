# Sales CRM voice agent example
import os
import sys
import asyncio
import argparse
import urllib.request
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.voice_agent import VoiceAgent
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.transcriptions.language import Language
from piopiy.services.piopiy_opensource.kokoro import KokoroTTSService


load_dotenv()


def download_if_missing(url: str, local_path: str):
    if not os.path.exists(local_path):
        print(f"Downloading {url} -> {local_path}")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        urllib.request.urlretrieve(url, local_path)
    else:
        print(f"File already exists: {local_path}")
    return local_path


def get_kokoro_model(choice: str = "normal"):
    base_dir = os.path.join(os.getcwd(), "kokoro_models")
    os.makedirs(base_dir, exist_ok=True)

    # Voices file (always required)
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
    voices_path = download_if_missing(voices_url, os.path.join(base_dir, "voices-v1.0.bin"))

    # Model file (choice-dependent)
    if choice == "normal":
        model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
        model_path = download_if_missing(model_url, os.path.join(base_dir, "kokoro-v1.0.onnx"))
    elif choice == "int8-cpu":
        model_url = "https://github.com/taylorchu/kokoro-onnx/releases/download/v0.2.0/kokoro-quant-convinteger.onnx"
        model_path = download_if_missing(model_url, os.path.join(base_dir, "kokoro-quant-convinteger.onnx"))
    elif choice == "int8-gpu":
        model_url = "https://github.com/taylorchu/kokoro-onnx/releases/download/v0.2.0/kokoro-quant-gpu.onnx"
        model_path = download_if_missing(model_url, os.path.join(base_dir, "kokoro-quant-gpu.onnx"))
    else:
        raise ValueError(f"Invalid choice '{choice}'. Use: normal | int8-cpu | int8-gpu")

    return model_path, voices_path

async def create_session():
   
    voice_agent = VoiceAgent(
        instructions=(
            "You are an advanced voice AI sales assistant for a CRM platform "
            "Your role is to engage with potential customers understand their needs "
            "and effectively communicate how our CRM solutions can address their challenges "
            "Provide clear concise and persuasive information to help them make informed decisions "
            "Always be courteous professional and ready to assist with any sales related inquiries"
        ),
    
        greeting="Hello Good Morning Welcome to TeleCMI, how can I help you today?"
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    #KokoroTTS
    model_path, voices_path = get_kokoro_model(args.model)
    tts = KokoroTTSService(

        model_path = model_path,
        voices_path = voices_path,
        voice_id = "af_sarah",
        is_phonemes = False,
        params=KokoroTTSService.InputParams(
            language=Language.EN,  
            speed=1.2,
        ),
    )
    
    vad = SileroVADAnalyzer()


    await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts, vad=vad, allow_interruptions=True, interruption_strategy=MinWordsInterruptionStrategy(min_words=1))
    await voice_agent.start()


   

async def main(args):
    agent = Agent(
        agent_id="AGENT_ID",
        agent_token="AGENT_TOKEN",
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sales CRM Voice Agent with Kokoro TTS")
    parser.add_argument(
        "--model",
        type = str,
        default="normal",
        choices = ["normal", "int8-cpu", "int8-gpu"],
        help="choose kokoro model type"
    )
    
    args = parser.parse_args()
    asyncio.run(main(args))

