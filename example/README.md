# Examples

This directory contains runnable voice agents that demonstrate how to combine different LLM, ASR, and TTS providers with the `VoiceAgent.configure()` API. Both **cascaded** (STT → LLM → TTS) and **speech-to-speech** (realtime models like Gemini Live) pipelines are shown — mix and match the scripts to learn how to wire up both managed services and open-source runtimes.

## Installation

Install the SDK with the providers you plan to test:

```bash
# Cloud quickstart stack (OpenAI LLM, Deepgram ASR, Cartesia TTS, Silero VAD)
pip install "piopiy-ai[cartesia,deepgram,openai,silero]" python-dotenv

# Open-source stack (Ollama LLM, Whisper ASR, Chatterbox TTS)
pip install "piopiy-ai[whisper]" python-dotenv
```

Some open-source samples require additional runtimes:

- [Ollama](https://ollama.ai) running locally for `OLLamaLLMService` and model downloads.
- A Chatterbox TTS WebSocket server for `ChatterboxTTSService` (see the project README for setup).
- `kokoro-onnx` models downloaded via `download-kokoro` or the automatic downloader.
- Custom WebSocket services for Orpheus or Ultravox where noted in each script.

## Environment variables

All examples expect credentials provided as environment variables. At minimum, export your Piopiy agent credentials:

```bash
export AGENT_ID=your_agent_id
export AGENT_TOKEN=your_agent_token
```

Set additional keys depending on the stack you run (for example `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`). Local-only stacks can omit cloud keys.

## Example matrix

| Example | LLM | ASR | TTS / Speech | Highlights |
|---------|-----|-----|--------------|------------|
| `basic/basic.py` | OpenAI | Deepgram | Cartesia | Minimal cascaded voice loop showcasing `VoiceAgent.configure()` with Silero VAD.
| `gemini_live/gemini_live_agent.py` | Gemini Live (realtime) | – | – | **Speech-to-speech** — model owns audio in and out (no STT/TTS).
| `opensource/cascaded.py` | Ollama (open-source) | Whisper (open-source) | Chatterbox (open-source) | **Fully open-source cascaded stack.** Local-first STT + LLM + TTS.
| `opensource/hybrid.py` | Ultravox (audio-LLM) | – | VibeVoice (open-source) | **Fully open-source audio-LLM hybrid.** Ultravox replaces STT+LLM; VibeVoice for output.
| `murf/murf_tts.py` | OpenAI | Deepgram | Murf.ai | High-quality natural voices with extensive customization.
| `mcp_sales/mcp_sales.py` | OpenAI | Deepgram | Cartesia | Adds MCP tools for function calling and knowledge retrieval.
| `function_calling/weather.py` | OpenAI | Deepgram | Cartesia | Weather tool-calling workflow.
| `function_calling/crm.py` | OpenAI | Deepgram | Cartesia | CRM sales assistant with structured tool outputs.
| `chatterbox/chatterbox_ws.py` | Ollama (open-source) | Whisper (open-source) | Chatterbox (open-source) | Streams speech from a fully open-source stack running locally.
| `kokoro/kokoro.py` | Ollama (open-source) | Whisper (open-source) | Kokoro (open-source) | Fully offline TTS using Kokoro ONNX models.
| `orpheus/orpheus.py` | Ollama (open-source) | Whisper (open-source) | Orpheus (open-source) | Demonstrates the pluggable VAD dictionary syntax with an OSS TTS engine.
| `ultravox/ultravox.py` | Ultravox (audio-LLM) | – | Deepgram | **Audio-LLM hybrid** — Ultravox replaces STT+LLM, external TTS speaks the reply.

## Running an example

Activate your virtual environment, export the required environment variables, then run a script:

```bash
python example/basic/basic.py
# or
python example/function_calling/weather.py
```

Refer to each script for provider-specific configuration such as local server URLs or extra dependencies. Thanks to Pipecat for making the SDK integration straightforward.
