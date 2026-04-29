# Supported Providers

Piopiy AI supports a wide range of providers across four categories:
**Realtime / Speech-to-Speech**, **LLM**, **STT**, and **TTS**.

> For the full constructor reference and runnable examples for every
> speech-to-speech model, see
> [docs/REALTIME_MODELS.md](REALTIME_MODELS.md).

## Realtime / Speech-to-Speech models

Audio-in, audio-out (or audio-in, text-out for hybrids). Plug into
`voice_agent.configure(llm=...)` with no `tts=` for pure S2S, or with
`tts=` for the audio-LLM hybrid case.

| Model | Class | Mode | Example |
|---|---|---|---|
| **Gemini Live** (Google) | `GeminiLiveLLMService` | S2S | [example/gemini_live/](../example/gemini_live/) |
| **OpenAI Realtime** | `OpenAIRealtimeLLMService` | S2S | [example/openai_realtime/](../example/openai_realtime/) |
| **Azure OpenAI Realtime** | `AzureRealtimeLLMService` | S2S | [example/azure_realtime/](../example/azure_realtime/) |
| **AWS Nova Sonic** | `AWSNovaSonicLLMService` | S2S | [example/aws_nova_sonic/](../example/aws_nova_sonic/) |
| **Grok Realtime** (xAI) | `GrokRealtimeLLMService` | S2S | [example/grok_realtime/](../example/grok_realtime/) |
| **Ultravox** (cloud) | `UltravoxRealtimeLLMService` | Audio-LLM hybrid | [example/ultravox/](../example/ultravox/) |
| **Ultravox** (open-source) | `UltravoxService` | Audio-LLM hybrid | [example/opensource/hybrid.py](../example/opensource/hybrid.py) |

## Cascaded providers (LLM, STT, TTS)

| Provider | Categories |
|---------|------------|
| [Anthropic](llm/anthropic.md) | LLM |
| [AssemblyAI](stt/assemblyai.md) | STT |
| [AsyncAI](tts/asyncai.md) | TTS |
| [AWS](llm/aws.md) | LLM, STT, TTS |
| [Azure](llm/azure.md) | LLM, STT, TTS |
| [Cartesia](stt/cartesia.md) | STT, TTS |
| [Cerebras](llm/cerebras.md) | LLM |
| [Deepgram](stt/deepgram.md) | STT, TTS |
| [DeepSeek](llm/deepseek.md) | LLM |
| [ElevenLabs](tts/elevenlabs.md) | TTS |
| [Fal](stt/fal.md) | STT |
| [Fireworks](llm/fireworks.md) | LLM |
| [Fish](tts/fish.md) | TTS |
| [Gladia](stt/gladia.md) | STT |
| [Google](llm/google.md) | LLM, STT, TTS |
| [Grok](llm/grok.md) | LLM |
| [Groq](llm/groq.md) | LLM, STT, TTS |
| [Inworld](tts/inworld.md) | TTS |
| [LMNT](tts/lmnt.md) | TTS |
| [Mistral](llm/mistral.md) | LLM |
| [Minimax](tts/minimax.md) | TTS |
| [Neuphonic](tts/neuphonic.md) | TTS |
| [NIM](llm/nim.md) | LLM |
| [Ollama](llm/ollama.md) | LLM |
| [OpenAI](llm/openai.md) | LLM, STT, TTS |
| [OpenPipe](llm/openpipe.md) | LLM |
| [OpenRouter](llm/openrouter.md) | LLM |
| [Perplexity](llm/perplexity.md) | LLM |
| [Piper](tts/piper.md) | TTS |
| [PlayHT](tts/playht.md) | TTS |
| [Qwen](llm/qwen.md) | LLM |
| [Rime](tts/rime.md) | TTS |
| [Riva](stt/riva.md) | STT, TTS |
| [SambaNova](llm/sambanova.md) | LLM, STT |
| [Sarvam](tts/sarvam.md) | TTS |
| [Soniox](stt/soniox.md) | STT |
| [Speechmatics](stt/speechmatics.md) | STT |
| [TeleCMI](transport/telecmi.md) | Transport |
| [Together](llm/together.md) | LLM |
| [Ultravox](stt/ultravox.md) | STT |
| [Whisper](stt/whisper.md) | STT |
| [XTTS](tts/xtts.md) | TTS |
