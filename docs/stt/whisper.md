# Whisper STT

```bash
pip install "piopiy-ai[whisper]"
export WHISPER_API_KEY=your_key
```

```python
import os
from piopiy.services.whisper.stt import WhisperSTTService

service = WhisperSTTService(api_key=os.getenv('WHISPER_API_KEY'))
```
