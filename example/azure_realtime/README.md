# Azure OpenAI Realtime — Speech-to-Speech Agent

OpenAI Realtime model surface deployed on Azure. Same voices and
`session_properties` as the OpenAI service, with Azure's authentication and
endpoint format.

See [docs/REALTIME_MODELS.md](../../docs/REALTIME_MODELS.md#3-azure-openai-realtime)
for the full constructor reference.

## Install

```bash
pip install "piopiy-ai[azure,silero]" python-dotenv
```

## Environment

```bash
AGENT_ID=...
AGENT_TOKEN=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_REALTIME_URL=wss://my-project.openai.azure.com/openai/realtime?api-version=2025-04-01-preview&deployment=my-realtime-deployment
```

The full Azure WSS URL includes `api-version` and `deployment` query parameters
— grab them from the deployment page in Azure AI Studio.

## Run

```bash
python example/azure_realtime/azure_realtime_agent.py
```

## Other realtime models

- [Gemini Live](../gemini_live/), [OpenAI Realtime](../openai_realtime/),
  [AWS Nova Sonic](../aws_nova_sonic/), [Grok Realtime](../grok_realtime/)
