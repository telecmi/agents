# OpenAI STT

```bash
pip install "piopiy-ai[openai]"
export OPENAI_API_KEY=your_key
```

```python
import os
from piopiy.services.openai.stt import OpenAISTTService

service = OpenAISTTService(api_key=os.getenv('OPENAI_API_KEY'))
```
