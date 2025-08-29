# XTTS TTS

```bash
pip install "piopiy-ai[xtts]"
export XTTS_API_KEY=your_key
```

### Parameters

- `voice_id`: Voice identifier to use
- `base_url`: Override API base URL
- `aiohttp_session`: Reuse existing aiohttp session
- `language`: Language selection (default `Language.EN`)
- `sample_rate`: Target audio sample rate

### Input Parameters

None

### Example

```python
import os
from piopiy.services.xtts.tts import XTTSService

tts = XTTSService(
    api_key=os.getenv("XTTS_API_KEY"),
    voice_id="VOICE_ID",
    language="EN",
    sample_rate=24000,
)
```
