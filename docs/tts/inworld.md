# Inworld TTS

```bash
pip install "piopiy-ai[inworld]"
export INWORLD_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `aiohttp_session`: Reuse existing aiohttp session
- `voice_id`: Voice identifier to use (default `"Ashley"`)
- `model`: Model name to use (default `"inworld-tts-1"`)
- `streaming`: Enable streaming mode (default `True`)
- `sample_rate`: Target audio sample rate
- `encoding`: Audio encoding (default `"LINEAR16"`)
- `params`: Provider specific options


### Input Parameters

- `temperature`: Voice temperature control

### Example

```python
import os
from piopiy.services.inworld.tts import InworldTTSService

tts = InworldTTSService(
    api_key=os.getenv("INWORLD_API_KEY"),
    voice_id="Ashley",
    model="inworld-tts-1",
    sample_rate=24000,
)
```
