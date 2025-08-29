# LMNT TTS

```bash
pip install "piopiy-ai[lmnt]"
export LMNT_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice_id`: Voice identifier to use
- `sample_rate`: Target audio sample rate
- `language`: Language selection (default `Language.EN`)
- `model`: Model name to use (default `"blizzard"`)


### Input Parameters

None


### Example

```python
import os
from piopiy.services.lmnt.tts import LmntTTSService

tts = LmntTTSService(
    api_key=os.getenv("LMNT_API_KEY"),
    voice_id="VOICE_ID",
    model="blizzard",
    sample_rate=24000,
)
```
