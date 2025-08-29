# Riva TTS

```bash
pip install "piopiy-ai[riva]"
export RIVA_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `server`: Parameter (default `"grpc.nvcf.nvidia.com:443"`)
- `voice_id`: Voice identifier to use (default `"Magpie-Multilingual.EN-US.Ray"`)
- `sample_rate`: Target audio sample rate
- `model_function_map`: Parameter (default `{
            "function_id": "877104f7-e885-42b9-8de8-f6e4c6303969",
            "model_name": "magpie-tts-multilingual",
        }`)
- `params`: Provider specific options


### Input Parameters

- `language`: Language code for synthesis
- `quality`: Audio quality setting


### Example

```python
import os
from piopiy.services.riva.tts import RivaTTSService

tts = RivaTTSService(
    api_key=os.getenv("RIVA_API_KEY"),
    server="grpc.nvcf.nvidia.com:443",
    voice_id="Magpie-Multilingual.EN-US.Ray",
    sample_rate=24000,
)
```
