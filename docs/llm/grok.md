# Grok LLM

```bash
pip install "piopiy-ai[grok]"
export GROK_API_KEY=your_key
```

```python
import os
from piopiy.services.grok.llm import GrokLLMService

service = GrokLLMService(api_key=os.getenv('GROK_API_KEY'))
```
