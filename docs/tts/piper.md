# Piper TTS

```bash
pip install "piopiy-ai[piper]"
export PIPER_API_KEY=your_key
```

```python
import os
from piopiy.services.piper.tts import PiperTTSService

service = PiperTTSService(api_key=os.getenv('PIPER_API_KEY'))
```
