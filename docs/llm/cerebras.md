# Cerebras LLM

```bash
pip install "piopiy-ai[cerebras]"
export CEREBRAS_API_KEY=your_key
```

```python
import os
from piopiy.services.cerebras.llm import CerebrasLLMService

service = CerebrasLLMService(api_key=os.getenv('CEREBRAS_API_KEY'))
```
