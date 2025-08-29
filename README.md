# agents
Build Telephonic-Grade Voice AI — WebRTC-Ready Framework

## Installation

Requires Python 3.10+.

```bash
pip install piopiy-ai
```

Optional extras:

```bash
pip install "piopiy-ai[openai,anthropic]"
```

## Running Tests

To run the test suite, install dependencies and execute:

```bash
pytest
```

## Running the Sales CRM Example

1. Install the required dependencies:

```bash
pip install "piopiy-ai[openai,deepgram,cartesia,silero]" python-dotenv
```

2. Create a `.env` file with the following variables:
   - `AGENT_ID`
   - `AGENT_TOKEN`
   - `DEEPGRAM_API_KEY`
   - `OPENAI_API_KEY`
   - `CARTESIA_API_KEY`
3. Launch the voice agent:

```bash
python example/sales.py
```

This starts a sales-focused CRM assistant ready to handle customer queries.

