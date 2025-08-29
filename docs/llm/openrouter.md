# OpenRouter LLM

```bash
pip install "piopiy-ai[openrouter]"
export OPENROUTER_API_KEY=your_key
```

```python
import os
from piopiy.services.openrouter.llm import OpenRouterLLMService

service = OpenRouterLLMService(api_key=os.getenv('OPENROUTER_API_KEY'))
```
