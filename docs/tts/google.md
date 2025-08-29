# Google TTS

```bash
pip install "piopiy-ai[google]"
export GOOGLE_API_KEY=your_key
```

```python
import os
from piopiy.services.google.tts import GoogleHttpTTSService

service = GoogleHttpTTSService(api_key=os.getenv('GOOGLE_API_KEY'))
```
