# XTTS TTS

```bash
pip install "piopiy-ai[xtts]"
export XTTS_API_KEY=your_key
```

```python
import os
from piopiy.services.xtts.tts import XTTSService

service = XTTSService(api_key=os.getenv('XTTS_API_KEY'))
```
