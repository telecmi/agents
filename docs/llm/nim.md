# NIM LLM

```bash
pip install "piopiy-ai[nim]"
export NIM_API_KEY=your_key
```

```python
import os
from piopiy.services.nim.llm import NimLLMService

service = NimLLMService(api_key=os.getenv('NIM_API_KEY'))
```
