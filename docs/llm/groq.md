# Groq LLM

```bash
pip install "piopiy-ai[groq]"
export GROQ_API_KEY=your_key
```

```python
import os
from piopiy.services.groq.llm import GroqLLMService
from piopiy.services.openai.base_llm import BaseOpenAILLMService

params = BaseOpenAILLMService.InputParams(
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.5,
    max_completion_tokens=256,
    extra={},
)

service = GroqLLMService(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    params=params,
)
```

### Optional Arguments

`GroqLLMService` accepts additional arguments:

- `model`: Groq model name. Defaults to `llama-3.3-70b-versatile`.
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

Customize `base_url` or `default_headers` when pointing the client to a proxy or self-hosted Groq-compatible endpoint.
