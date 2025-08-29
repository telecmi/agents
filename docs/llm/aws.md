# AWS LLM

```bash
pip install "piopiy-ai[aws]"
export AWS_API_KEY=your_key
```

```python
import os
from piopiy.services.aws.llm import AWSBedrockLLMService

service = AWSBedrockLLMService(api_key=os.getenv('AWS_API_KEY'))
```
