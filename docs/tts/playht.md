# PlayHT TTS

```bash
pip install "piopiy-ai[playht]"
export PLAYHT_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `user_id`: User identifier
- `voice_url`: Voice URL
- `voice_engine`: Voice engine ID (default `"Play3.0-mini"`)
- `sample_rate`: Target audio sample rate
- `output_format`: Output audio format (default `"wav"`)
- `params`: Provider specific options


### Input Parameters

- `language`: Language for synthesis
- `speed`: Speech speed multiplier
- `seed`: Random seed for voice consistency


### Example

```python
import os
from piopiy.services.playht.tts import PlayHTTTSService

tts = PlayHTTTSService(
    api_key=os.getenv("PLAYHT_API_KEY"),
    user_id="USER_ID",
    voice_engine="Play3.0-mini",
    sample_rate=24000,
)
```
