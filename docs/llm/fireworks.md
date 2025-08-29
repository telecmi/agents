# Fireworks LLM

```bash
pip install "piopiy-ai[fireworks]"
export FIREWORKS_API_KEY=your_key
```

```python
import os
from piopiy.services.fireworks.llm import FireworksLLMService

service = FireworksLLMService(api_key=os.getenv('FIREWORKS_API_KEY'))
```
