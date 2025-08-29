# Ollama LLM

```bash
pip install "piopiy-ai[ollama]"
export OLLAMA_API_KEY=your_key
```

```python
import os
from piopiy.services.ollama.llm import OLLamaLLMService
from piopiy.services.openai.base_llm import BaseOpenAILLMService

params = BaseOpenAILLMService.InputParams(
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.5,
    max_completion_tokens=256,
    extra={},
)

service = OLLamaLLMService(
    api_key=os.getenv("OLLAMA_API_KEY"),
    model="llama2",
    params=params,
)
```

### Optional Arguments

`OLLamaLLMService` accepts additional arguments:

- `model`: Ollama model name. Defaults to `llama2`.
- `base_url`: Custom API endpoint, useful for self-hosted proxies.
- `organization` and `project`: IDs used for multi-tenant setups.
- `default_headers`: Extra headers sent with each request.
- `retry_timeout_secs`: Request timeout in seconds.
- `retry_on_timeout`: Retry once if a request times out.

### Input Parameters

`BaseOpenAILLMService.InputParams` controls sampling and limits:

- `temperature`: Higher values produce more random outputs.
- `top_p`: Nucleus sampling; alternative to `temperature`.
- `frequency_penalty`: Discourage repeated tokens.
- `max_completion_tokens`: Cap the length of the LLM's reply.
- `extra`: Dictionary for model-specific options.

Pass these via the `params` argument when creating the service, as shown above.

### Custom Endpoints and Headers

Customize `base_url` or `default_headers` when pointing the client to a proxy or self-hosted Ollama-compatible endpoint.
