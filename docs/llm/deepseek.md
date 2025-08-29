# DeepSeek LLM

```bash
pip install "piopiy-ai[deepseek]"
export DEEPSEEK_API_KEY=your_key
```

```python
import os
from piopiy.services.deepseek.llm import DeepSeekLLMService

service = DeepSeekLLMService(api_key=os.getenv('DEEPSEEK_API_KEY'))
```
