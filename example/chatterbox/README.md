# Chatterbox Client Agent Example

## ⚙️ Requirements

- **Python 3.11** (recommended)  
- A running **Chatterbox TTS server** (`ws://server_ip:port`)  
- Change the base url of TTS service 
- Create a .env file and place it inside the root folder and the API keys are:
  - `DEEPGRAM_API_KEY` : [Deepgram](https://deepgram.com)
  - `OPENAI_API_KEY` : [OpenAI](https://platform.openai.com) 
  - `AGENT_ID` : from TeleCMI 
  - `AGENT_TOKEN` : from TeleCMI

---

## 📦 Installation

1. (Optional) Create and activate a virtual environment:

   ```bash
   python3.11 -m venv chatterbox_env
   source chatterbox_env/bin/activate   # On Windows: chatterbox_env\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install "piopiy-ai[deepgram,openai,silero]" python-dotenv
   ```

---

## 🔑 Environment Setup

Create a `.env` file in the project root with the following values:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token
```

---

## ▶️ Running the Agent

Run the voice agent with:

```bash
python chatterbox_ws.py
```
