# Fish TTS

```bash
pip install "piopiy-ai[fish]"
export FISH_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `reference_id`: Reference audio identifier
- `model`: Model name to use
- `model_id`: Model identifier to use (default `"speech-1.5"`)
- `output_format`: Output audio format (default `"pcm"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options


### Input Parameters

- `language`: Language for synthesis
- `latency`: Latency mode ("normal" or "balanced")
- `normalize`: Whether to normalize audio output
- `prosody_speed`: Speech speed multiplier
- `prosody_volume`: Volume adjustment in dB


### Example

```python
import os
from piopiy.services.fish.tts import FishAudioTTSService

tts = FishAudioTTSService(
    api_key=os.getenv("FISH_API_KEY"),
    reference_id="VOICE_ID",
    model_id="speech-1.5",
    sample_rate=24000,
)
```
