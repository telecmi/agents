# Gemini Live (Speech-to-Speech) WebRTC/WebSocket Example

This directory contains an example of how to orchestrate a natively conversational AI agent using Google's **Gemini Multimodal Live** (Speech-to-Speech) API with Piopiy AI.

Because Gemini Live handles both listening to your voice and synthesizing voice responses natively, this example **does not** require traditional Speech-to-Text (STT) or Text-to-Speech (TTS) services.

## Prerequisites

1. Install the required dependencies:
   ```bash
   pip install "piopiy-ai[google]" python-dotenv
   ```

2. Setup your Environment Variables. Create a `.env` file in your project root with the following:
   ```env
   AGENT_ID=your_telecmi_agent_id
   AGENT_TOKEN=your_telecmi_agent_token
   GOOGLE_API_KEY=your_google_ai_studio_api_key
   ```
   *Note: You can get a free Google API key from [Google AI Studio](https://aistudio.google.com/).*

## Running the Example

Start the agent:
```bash
python example/gemini_live/gemini_live.py
```

Once running, the Agent will automatically answer incoming calls (or WebRTC / WebSocket connections) routed through your Piopiy TeleCMI application, and connect you with Gemini Live for a high-quality, ultra-low-latency real-time voice conversation.
