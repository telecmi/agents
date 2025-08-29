# AWS TTS

```bash
pip install "piopiy-ai[aws]"
export AWS_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `aws_access_key_id`: AWS access key ID
- `aws_session_token`: AWS session token
- `region`: Region for the service
- `voice_id`: Voice identifier to use (default `"Joanna"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options


### Input Parameters

- `engine`: TTS engine to use (e.g., "standard", "neural")
- `language`: Language for synthesis
- `pitch`: Voice pitch adjustment
- `rate`: Speech rate adjustment
- `volume`: Voice volume adjustment
- `lexicon_names`: Pronunciation lexicons to apply


### Example

```python
import os
from piopiy.services.aws.tts import AWSPollyTTSService

tts = AWSPollyTTSService(
    api_key=os.getenv("AWS_API_KEY"),
    region="us-east-1",
    voice_id="Joanna",
    sample_rate=24000,
)
```
