# Speechmatics STT

```bash
pip install "piopiy-ai[speechmatics]"
export SPEECHMATICS_API_KEY=your_key
```

```python
import os
from piopiy.services.speechmatics.stt import SpeechmaticsSTTService

service = SpeechmaticsSTTService(api_key=os.getenv('SPEECHMATICS_API_KEY'))
```
