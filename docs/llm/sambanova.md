# SambaNova LLM

```bash
pip install "piopiy-ai[sambanova]"
export SAMBANOVA_API_KEY=your_key
```

```python
import os
from piopiy.services.sambanova.llm import SambaNovaLLMService

service = SambaNovaLLMService(api_key=os.getenv('SAMBANOVA_API_KEY'))
```
