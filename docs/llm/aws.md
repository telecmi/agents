# AWS LLM

```bash
pip install "piopiy-ai[aws]"
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

```python
import os
from piopiy.services.aws.llm import AWSBedrockLLMService

params = AWSBedrockLLMService.InputParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=256,
)

service = AWSBedrockLLMService(
    model="amazon.nova-pro-v1:0",
    aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_region="us-east-1",
    params=params,
)
```

### Optional Arguments

`AWSBedrockLLMService` accepts additional arguments:

- `aws_access_key` and `aws_secret_key`: AWS credentials; use IAM roles if omitted.
- `aws_session_token`: Token for temporary credentials.
- `aws_region`: AWS region for the Bedrock service.
- `client_config`: Custom boto3 client configuration.
- `retry_timeout_secs`: Request timeout in seconds.
- `retry_on_timeout`: Retry once if a request times out.

### Input Parameters

`AWSBedrockLLMService.InputParams` controls sampling and limits:

- `temperature`: Higher values produce more random outputs.
- `top_p`: Nucleus sampling; alternative to `temperature`.
- `max_tokens`: Cap the length of the LLM's reply.
- `stop_sequences`: Strings that halt generation.
- `latency`: Choose between `standard` and `optimized` modes.
- `additional_model_request_fields`: Dictionary for model-specific options.

Pass these via the `params` argument when creating the service, as shown above.

### Custom Clients

Provide `client_config` to tune networking or retry behavior when connecting to Bedrock.
