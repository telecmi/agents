# Together LLM

```bash
pip install "piopiy-ai[together]"
export TOGETHER_API_KEY=your_key
```

```python
import os
from piopiy.services.together.llm import TogetherLLMService

service = TogetherLLMService(api_key=os.getenv('TOGETHER_API_KEY'))
```
