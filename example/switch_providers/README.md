# Service Switching Examples

This folder contains examples demonstrating how to switch between different AI providers at runtime using the `ServiceSwitcher` pipeline component.

## Getting Started

### 1. Installation

First, install the `piopiy-ai` package using pip. Since these examples use specific providers (Cartesia, ElevenLabs, Deepgram, Speechmatics), you should install the package with the necessary extras.

```bash
# Install with all relevant extras for these examples
pip install "piopiy-ai[cartesia,elevenlabs,deepgram,speechmatics]"
```

*Note: You may need to use quotes around the package name with brackets in some shells (like zsh).*

### 2. Environment Setup

You need to set up your API keys. You can set them as environment variables or create a `.env` file in your project directory.

**Required Keys:**

```bash
AGENT_ID=your_piopiy_agent_id
AGENT_TOKEN=your_piopiy_agent_token
OPENAI_API_KEY=sk-...
CARTESIA_API_KEY=...
ELEVENLABS_API_KEY=...
DEEPGRAM_API_KEY=...
SPEECHMATICS_API_KEY=...
```

### 3. Running the Examples

Once installed and configured, you can run the python scripts directly.

---

## Examples provided

### 1. TTS Switching (`tts_switch.py`)

This example allows you to switch the **Text-to-Speech (TTS)** provider between **Cartesia** and **ElevenLabs** during a live call.

**Run:**
```bash
python tts_switch.py
```

**What to say:**
- "Switch to ElevenLabs"
- "Switch to Cartesia"
- "Change my voice to ElevenLabs"

### 2. STT Switching (`stt_switch.py`)

This example allows you to switch the **Speech-to-Text (STT)** provider between **Deepgram** and **Speechmatics** during a live call.

**Run:**
```bash
python stt_switch.py
```

**What to say:**
- "Switch to Speechmatics"
- "Switch to Deepgram"
- "Change my hearing to Speechmatics"

## How it Works

Both examples use a tool (function call) defined in the code (e.g., `manualswitch`) to interpret your request and trigger the `voice_agent.switch_service()` method.

The `ServiceSwitcher` handles the underlying logic of swapping the active service component in the processing pipeline immediately.
