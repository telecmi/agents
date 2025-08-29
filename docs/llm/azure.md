# Azure LLM

```bash
pip install "piopiy-ai[azure]"
export AZURE_API_KEY=your_key
```

```python
import os
from piopiy.services.azure.llm import AzureLLMService
from piopiy.services.openai.base_llm import BaseOpenAILLMService

params = BaseOpenAILLMService.InputParams(
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.5,
    max_completion_tokens=256,
    extra={},
)

service = AzureLLMService(
    api_key=os.getenv("AZURE_API_KEY"),
    endpoint="https://your-endpoint.openai.azure.com",
    model="gpt-4o-mini",
    params=params,
)
```

### Optional Arguments

`AzureLLMService` accepts additional arguments:

- `endpoint`: Azure OpenAI endpoint URL.
- `model`: Deployment name for the model.
- `api_version`: Azure API version. Defaults to `2024-09-01-preview`.
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

Set `endpoint` to your Azure deployment URL and use `default_headers` for enterprise proxies or additional authentication.
