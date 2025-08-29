# Riva TTS

```bash
pip install "piopiy-ai[riva]"
export RIVA_API_KEY=your_key
```

```python
import os
from piopiy.services.riva.tts import RivaTTSService

service = RivaTTSService(api_key=os.getenv('RIVA_API_KEY'))
```
