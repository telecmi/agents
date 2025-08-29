# Groq TTS

```bash
pip install "piopiy-ai[groq]"
export GROQ_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `output_format`: Output audio format (default `"wav"`)
- `params`: Provider specific options
- `model_name`: Model name to use (default `"playai-tts"`)
- `voice_id`: Voice identifier to use (default `"Celeste-PlayAI"`)
- `sample_rate`: Target audio sample rate (default `GROQ_SAMPLE_RATE`)


### Input Parameters

- `language`: Language for synthesis
- `speed`: Speech speed multiplier


### Example

```python
import os
from piopiy.services.groq.tts import GroqTTSService

tts = GroqTTSService(
    api_key=os.getenv("GROQ_API_KEY"),
    voice_id="Celeste-PlayAI",
    model_name="playai-tts",
    output_format="wav",
)
```
