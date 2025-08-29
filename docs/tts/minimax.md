# MiniMax TTS

```bash
pip install "piopiy-ai[minimax]"
export MINIMAX_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `base_url`: Override API base URL (default `"https://api.minimax.io/v1/t2a_v2"`)
- `group_id`: Group identifier
- `model`: Model name to use (default `"speech-02-turbo"`)
- `voice_id`: Voice identifier to use (default `"Calm_Woman"`)
- `aiohttp_session`: Reuse existing aiohttp session
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options


### Input Parameters

- `language`: Language for synthesis
- `speed`: Speech speed (0.5 to 2.0)
- `volume`: Speech volume (0 to 10)
- `pitch`: Pitch adjustment (-12 to 12)
- `emotion`: Emotional tone (e.g., "happy", "sad")
- `english_normalization`: Enable English text normalization


### Example

```python
import os
from piopiy.services.minimax.tts import MiniMaxHttpTTSService

tts = MiniMaxHttpTTSService(
    api_key=os.getenv("MINIMAX_API_KEY"),
    group_id="GROUP_ID",
    model="speech-02-turbo",
    voice_id="Calm_Woman",
    sample_rate=24000,
)
```
