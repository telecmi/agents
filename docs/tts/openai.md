# OpenAI TTS

```bash
pip install "piopiy-ai[openai]"
export OPENAI_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `base_url`: Override API base URL
- `voice`: Voice identifier to use (default `"alloy"`)
- `model`: Model name to use (default `"gpt-4o-mini-tts"`)
- `sample_rate`: Target audio sample rate
- `instructions`: Guidance for synthesis


### Input Parameters

None


### Example

```python
import os
from piopiy.services.openai.tts import OpenAITTSService

tts = OpenAITTSService(
    api_key=os.getenv("OPENAI_API_KEY"),
    voice="alloy",
    model="gpt-4o-mini-tts",
    sample_rate=24000,
)
```
