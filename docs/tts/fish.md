# Fish TTS

```bash
pip install "piopiy-ai[fish]"
export FISH_API_KEY=your_key
```

```python
import os
from piopiy.services.fish.tts import FishAudioTTSService

service = FishAudioTTSService(api_key=os.getenv('FISH_API_KEY'))
```
