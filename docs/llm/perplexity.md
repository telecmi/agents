# Perplexity LLM

```bash
pip install "piopiy-ai[perplexity]"
export PERPLEXITY_API_KEY=your_key
```

```python
import os
from piopiy.services.perplexity.llm import PerplexityLLMService

service = PerplexityLLMService(api_key=os.getenv('PERPLEXITY_API_KEY'))
```
