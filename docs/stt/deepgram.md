# Deepgram STT

```bash
pip install "piopiy-ai[deepgram]"
export DEEPGRAM_API_KEY=your_key
```

```python
import os
from piopiy.services.deepgram.stt import DeepgramSTTService

service = DeepgramSTTService(api_key=os.getenv('DEEPGRAM_API_KEY'))
```
