# Neuphonic TTS

```bash
pip install "piopiy-ai[neuphonic]"
export NEUPHONIC_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice_id`: Voice identifier to use
- `url`: Endpoint URL (default `"wss://api.neuphonic.com"`)
- `sample_rate`: Target audio sample rate (default `22050`)
- `encoding`: Audio encoding (default `"pcm_linear"`)
- `params`: Provider specific options
- `aggregate_sentences`: Aggregate sentences before synthesis (default `True`)


### Input Parameters

- `language`: Language for synthesis
- `speed`: Speech speed multiplier


### Example

```python
import os
from piopiy.services.neuphonic.tts import NeuphonicTTSService

tts = NeuphonicTTSService(
    api_key=os.getenv("NEUPHONIC_API_KEY"),
    voice_id="VOICE_ID",
    sample_rate=22050,
    encoding="pcm_linear",
)
```
