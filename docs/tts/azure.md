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


### Input Parameters

- `emphasis`: Emphasis level for speech
- `language`: Language for synthesis
- `pitch`: Voice pitch adjustment
- `rate`: Speech rate multiplier
- `role`: Voice role for expression
- `style`: Speaking style
- `style_degree`: Intensity of the speaking style
- `volume`: Volume level


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
