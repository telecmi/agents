# Examples

This directory contains runnable voice agents that demonstrate how to combine different LLM, ASR, and TTS providers with the `VoiceAgent.Action` API. Mix and match the scripts to learn how to wire up both managed services and open-source runtimes.

## Installation

Install the SDK with the providers you plan to test:

```bash
# Cloud quickstart stack (OpenAI LLM, Deepgram ASR, Cartesia TTS, Silero VAD)
pip install "piopiy-ai[cartesia,deepgram,openai,silero]"

# Open-source stack (Ollama LLM, Whisper ASR, Chatterbox TTS)
pip install "piopiy-ai[whisper]"
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
| `basic.py` | OpenAI | Deepgram | Cartesia | Minimal voice loop showcasing `VoiceAgent.Action` with Silero VAD.
| `mcp_sales.py` | OpenAI | Deepgram | Cartesia | Adds MCP tools for function calling and knowledge retrieval.
| `function_calling/weather.py` | OpenAI | Deepgram | Cartesia | Weather tool-calling workflow.
| `function_calling/crm.py` | OpenAI | Deepgram | Cartesia | CRM sales assistant with structured tool outputs.
| `chatterbox/chatterbox_ws.py` | Ollama (open-source) | Whisper (open-source) | Chatterbox (open-source) | Streams speech from a fully open-source stack running locally.
| `kokoro/kokoro.py` | Ollama (open-source) | Whisper (open-source) | Kokoro (open-source) | Fully offline TTS using Kokoro ONNX models.
| `orpheus/orpheus.py` | Ollama (open-source) | Whisper (open-source) | Orpheus (open-source) | Demonstrates the pluggable VAD dictionary syntax with an OSS TTS engine.
| `ultravox/ultravox.py` | Ultravox omni runtime | – | Cartesia | Uses `SpeechAgent` with an all-in-one speech model and optional TTS override.

## Running an example

Activate your virtual environment, export the required environment variables, then run a script:

```bash
python basic.py
# or
python function_calling/weather.py
```

Refer to each script for provider-specific configuration such as local server URLs or extra dependencies. Thanks to Pipecat for making the SDK integration straightforward.
