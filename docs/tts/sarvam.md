# Sarvam TTS

```bash
pip install "piopiy-ai[sarvam]"
export SARVAM_API_KEY=your_key
```

```python
import os
from piopiy.services.sarvam.tts import SarvamHttpTTSService

service = SarvamHttpTTSService(api_key=os.getenv('SARVAM_API_KEY'))
```
