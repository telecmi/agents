# Google LLM

```bash
pip install "piopiy-ai[google]"
export GOOGLE_API_KEY=your_key
```

```python
import os
from piopiy.services.google.llm import GoogleLLMService

service = GoogleLLMService(api_key=os.getenv('GOOGLE_API_KEY'))
```
