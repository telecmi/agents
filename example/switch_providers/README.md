# Switch Providers Dynamically

This example demonstrates the advanced power of the Piopiy Voice AI Orchestrator's native `ServiceSwitcher`. 

Using a custom tool called `manualswitch`, the Voice Agent has the ability to change its own brain—or in this case, its Text-to-Speech (TTS) voice—on the fly mid-conversation based on user requests!

## How It Works

1. We initialize **two** different TTS services (Cartesia and ElevenLabs).
2. We wrap them in a `ServiceSwitcher(strategy_type=ServiceSwitcherStrategyManual)`.
3. We define a tool that the LLM can call to trigger `await voice_agent.switch_service(target_service)`.

## Requirements

You must install the SDK with the relevant provider extras:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,elevenlabs,silero]" python-dotenv
```

Your `.env` file must contain these keys:

```bash
AGENT_ID="your_agent_id"
AGENT_TOKEN="your_agent_token"
OPENAI_API_KEY="your_openai_key"
DEEPGRAM_API_KEY="your_deepgram_key"
CARTESIA_API_KEY="your_cartesia_key"
ELEVENLABS_API_KEY="your_elevenlabs_key"
```

## Running the Agent

Start the worker script to handle incoming calls:

```bash
python tts_switch.py
```

1. Log in to the **[Piopiy Dashboard](https://dashboard.telecmi.com)**.
2. Ensure you have purchased a Piopiy phone number and mapped it to your new AI Agent.
3. **Dial that phone number** from your personal phone to interact with your local agent!

*Try asking the agent to "change to the British voice" or "switch to the ElevenLabs voice"!*
