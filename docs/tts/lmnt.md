# LMNT TTS

```bash
pip install "piopiy-ai[lmnt]"
export LMNT_API_KEY=your_key
```

```python
import os
from piopiy.services.lmnt.tts import LmntTTSService

service = LmntTTSService(api_key=os.getenv('LMNT_API_KEY'))
```
