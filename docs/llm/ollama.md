# Ollama LLM

```bash
pip install "piopiy-ai[ollama]"
export OLLAMA_API_KEY=your_key
```

```python
import os
from piopiy.services.ollama.llm import OLLamaLLMService

service = OLLamaLLMService(api_key=os.getenv('OLLAMA_API_KEY'))
```
