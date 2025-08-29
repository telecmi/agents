# Qwen LLM

```bash
pip install "piopiy-ai[qwen]"
export QWEN_API_KEY=your_key
```

```python
import os
from piopiy.services.qwen.llm import QwenLLMService

service = QwenLLMService(api_key=os.getenv('QWEN_API_KEY'))
```
