# PlayHT TTS

```bash
pip install "piopiy-ai[playht]"
export PLAYHT_API_KEY=your_key
```

```python
import os
from piopiy.services.playht.tts import PlayHTTTSService

service = PlayHTTTSService(api_key=os.getenv('PLAYHT_API_KEY'))
```
