# Examples

This directory contains runnable example scripts for Piopiy AI.

- `sales.py` – complete voice agent.
- `function_calling/` – showcases tool/function calling with:
  - `crm.py`
  - `weather.py`

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
python sales.py
python function_calling/crm.py
python function_calling/weather.py
```

Thanks to Pepicat for making SDK usage easy.
