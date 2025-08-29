# Mistral LLM

```bash
pip install "piopiy-ai[mistral]"
export MISTRAL_API_KEY=your_key
```

```python
import os
from piopiy.services.mistral.llm import MistralLLMService

service = MistralLLMService(api_key=os.getenv('MISTRAL_API_KEY'))
```
