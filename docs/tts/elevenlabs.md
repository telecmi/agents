# ElevenLabs TTS

```bash
pip install "piopiy-ai[elevenlabs]"
export ELEVENLABS_API_KEY=your_key
```

```python
import os
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

service = ElevenLabsTTSService(api_key=os.getenv('ELEVENLABS_API_KEY'))
```
