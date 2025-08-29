# Rime TTS

```bash
pip install "piopiy-ai[rime]"
export RIME_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice_id`: Voice identifier to use
- `url`: Endpoint URL (default `"wss://users.rime.ai/ws2"`)
- `model`: Model name to use (default `"mistv2"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options
- `text_aggregator`: Custom text aggregator
- `aggregate_sentences`: Aggregate sentences before synthesis (default `True`)


### Input Parameters

- `language`: Language for synthesis
- `speed_alpha`: Speech speed multiplier
- `reduce_latency`: Reduce latency at potential quality cost
- `pause_between_brackets`: Add pauses between bracketed content
- `phonemize_between_brackets`: Phonemize bracketed content


### Example

```python
import os
from piopiy.services.rime.tts import RimeTTSService

tts = RimeTTSService(
    api_key=os.getenv("RIME_API_KEY"),
    voice_id="VOICE_ID",
    model="mistv2",
    sample_rate=24000,
)
```
