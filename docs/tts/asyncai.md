# AsyncAI TTS

```bash
pip install "piopiy-ai[asyncai]"
export ASYNCAI_API_KEY=your_key
```

```python
import os
from piopiy.services.asyncai.tts import AsyncAITTSService

service = AsyncAITTSService(api_key=os.getenv('ASYNCAI_API_KEY'))
```
