# Examples

This directory contains runnable example scripts for Piopiy AI.

- `basic.py` – minimal voice agent showing core setup.
- `sales.py` – complete voice agent.

## Install

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]"
```

## Configure

Set required credentials:

```bash
export AGENT_ID=your_agent_id
export AGENT_TOKEN=your_agent_token
export CARTESIA_API_KEY=your_cartesia_key
export DEEPGRAM_API_KEY=your_deepgram_key
export OPENAI_API_KEY=your_openai_key
```

## Run

Choose an example to run:

```bash
python basic.py
python sales.py
```

Thanks to Pepicat for making SDK usage easy.
