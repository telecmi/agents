# Google TTS

```bash
pip install "piopiy-ai[google]"
export GOOGLE_API_KEY=your_key
```

### Parameters

- `credentials`: Parameter
- `credentials_path`: Parameter
- `voice_id`: Voice identifier to use (default `"en-US-Chirp3-HD-Charon"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options

### Example

```python
import os
from piopiy.services.google.tts import GoogleHttpTTSService

tts = GoogleHttpTTSService(
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    voice_id="en-US-Chirp3-HD-Charon",
    sample_rate=24000,
)
```
