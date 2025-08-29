# Google LLM

```bash
pip install "piopiy-ai[google]"
export GOOGLE_API_KEY=your_key
```

```python
import os
from piopiy.services.google.llm import GoogleLLMService

params = GoogleLLMService.InputParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=256,
    extra={},
)

service = GoogleLLMService(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.0-flash",
    params=params,
)
```

### Optional Arguments

`GoogleLLMService` accepts additional arguments:

- `model`: Gemini model name. Defaults to `gemini-2.0-flash`.
- `system_instruction`: Optional system prompt for the model.
- `tools` and `tool_config`: Define and configure available functions.
- `http_options`: Customize HTTP behavior (proxies, timeouts).
- `retry_timeout_secs`: Request timeout in seconds.
- `retry_on_timeout`: Retry once if a request times out.

### Input Parameters

`GoogleLLMService.InputParams` controls sampling and limits:

- `temperature`: Higher values produce more random outputs.
- `top_p`: Nucleus sampling; alternative to `temperature`.
- `top_k`: Consider only the top-k tokens at each step.
- `max_tokens`: Cap the length of the LLM's reply.
- `extra`: Dictionary for model-specific options.

Pass these via the `params` argument when creating the service, as shown above.

### Custom HTTP Options

Provide `http_options` to route through proxies or adjust network settings for Google's API.
