# Sarvam TTS

```bash
pip install "piopiy-ai[sarvam]"
export SARVAM_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `aiohttp_session`: Reuse existing aiohttp session
- `voice_id`: Voice identifier to use (default `"anushka"`)
- `model`: Model name to use (default `"bulbul:v2"`)
- `base_url`: Override API base URL (default `"https://api.sarvam.ai"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options


### Input Parameters

- `language`: Language for synthesis
- `pitch`: Voice pitch adjustment
- `pace`: Speech pace multiplier
- `loudness`: Volume multiplier
- `enable_preprocessing`: Enable text preprocessing


### Example

```python
import os
from piopiy.services.sarvam.tts import SarvamHttpTTSService

tts = SarvamHttpTTSService(
    api_key=os.getenv("SARVAM_API_KEY"),
    voice_id="anushka",
    model="bulbul:v2",
    base_url="https://api.sarvam.ai",
    sample_rate=24000,
)
```
