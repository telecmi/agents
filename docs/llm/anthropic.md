# Anthropic LLM

```bash
pip install "piopiy-ai[anthropic]"
export ANTHROPIC_API_KEY=your_key
```

```python
import os
from piopiy.services.anthropic.llm import AnthropicLLMService

params = AnthropicLLMService.InputParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=256,
    extra={},
)

service = AnthropicLLMService(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-sonnet-4-20250514",
    params=params,
)
```

### Optional Arguments

`AnthropicLLMService` accepts additional arguments:

- `model`: Anthropic model name. Defaults to `claude-sonnet-4-20250514`.
- `client`: Custom `AsyncAnthropic` client instance.
- `retry_timeout_secs`: Request timeout in seconds.
- `retry_on_timeout`: Retry once if a request times out.

### Input Parameters

`AnthropicLLMService.InputParams` controls sampling and limits:

- `temperature`: Higher values produce more random outputs.
- `top_p`: Nucleus sampling; alternative to `temperature`.
- `max_tokens`: Cap the length of the LLM's reply.
- `enable_prompt_caching_beta`: Toggle Anthropic's prompt caching.
- `top_k`: Consider only the top-k tokens at each step.
- `extra`: Dictionary for model-specific options.

Pass these via the `params` argument when creating the service, as shown above.

### Custom Clients

Customize the `client` argument to point at alternate deployments or proxies compatible with Anthropic's API.
