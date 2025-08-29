# Ultravox STT

```bash
pip install "piopiy-ai[ultravox]"
export ULTRAVOX_API_KEY=your_key
```

```python
import os
from piopiy.services.ultravox.stt import UltravoxSTTService

service = UltravoxSTTService(api_key=os.getenv('ULTRAVOX_API_KEY'))
```
