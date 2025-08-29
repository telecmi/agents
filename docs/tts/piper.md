# Piper TTS

```bash
pip install "piopiy-ai[piper]"
export PIPER_API_KEY=your_key
```

### Parameters

- `base_url`: Override API base URL
- `aiohttp_session`: Reuse existing aiohttp session
- `sample_rate`: Target audio sample rate


### Input Parameters

None


### Example

```python
import aiohttp
from piopiy.services.piper.tts import PiperTTSService

session = aiohttp.ClientSession()
tts = PiperTTSService(
    base_url="http://localhost:5002",
    aiohttp_session=session,
    sample_rate=24000,
)
```
