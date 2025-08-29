# Rime TTS

```bash
pip install "piopiy-ai[rime]"
export RIME_API_KEY=your_key
```

```python
import os
from piopiy.services.rime.tts import RimeTTSService

service = RimeTTSService(api_key=os.getenv('RIME_API_KEY'))
```
