# Anthropic LLM

```bash
pip install "piopiy-ai[anthropic]"
export ANTHROPIC_API_KEY=your_key
```

```python
import os
from piopiy.services.anthropic.llm import AnthropicLLMService

service = AnthropicLLMService(api_key=os.getenv('ANTHROPIC_API_KEY'))
```
