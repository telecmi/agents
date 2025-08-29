# Deepgram TTS

```bash
pip install "piopiy-ai[deepgram]"
export DEEPGRAM_API_KEY=your_key
```

```python
import os
from piopiy.services.deepgram.tts import DeepgramTTSService

service = DeepgramTTSService(api_key=os.getenv('DEEPGRAM_API_KEY'))
```
