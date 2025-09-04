# Sales CRM voice agent example
import asyncio
from piopiy.agent import Agent
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.voice_agent import VoiceAgent
from dotenv import load_dotenv
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.transcriptions.language import Language

from piopyi.services.opensource.kokoro import KokoroTTSService
# from piopyi.services.piopyi_opensource.chatterbox import ChatterboxTTSService

load_dotenv()
import os

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

    #Cartesia
    #tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"), voice_id="bdab08ad-4137-4548-b9db-6142854c7525")

    #KokoroTTS
    ''' 
        Download these files
            You can download these model related files and put in your directory 
            MODEL PATH (choose any model you want to run with):
            https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
            INT8 CPU -> https://github.com/taylorchu/kokoro-onnx/releases/download/v0.2.0/kokoro-quant-convinteger.onnx
            INT8  GPU-> https://github.com/taylorchu/kokoro-onnx/releases/download/v0.2.0/kokoro-quant-gpu.onnx

            #wget -O kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
            #curl -L -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx

        VOICES PATH:
            https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

    '''
    tts = KokoroTTSService(

        model_path = "MODEL PATH",
        voices_path = "VOICES PATH",
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


   

async def main():
    agent = Agent(
        agent_id="AGENT_ID",
        agent_token="AGENT_TOKEN",
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    print(os.getenv("AGENT_ID"))
    asyncio.run(main())

