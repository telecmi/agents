# Azure TTS

```bash
pip install "piopiy-ai[azure]"
export AZURE_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `region`: Region for the service
- `voice`: Voice identifier to use (default `"en-US-SaraNeural"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options

### Example

```python
import os
from piopiy.services.azure.tts import AzureBaseTTSService

tts = AzureBaseTTSService(
    api_key=os.getenv("AZURE_API_KEY"),
    region="eastus",
    voice="en-US-SaraNeural",
    sample_rate=24000,
)
```
