# Inworld TTS

```bash
pip install "piopiy-ai[inworld]"
export INWORLD_API_KEY=your_key
```

```python
import os
from piopiy.services.inworld.tts import InworldTTSService

service = InworldTTSService(api_key=os.getenv('INWORLD_API_KEY'))
```
