# Soniox STT

```bash
pip install "piopiy-ai[soniox]"
export SONIOX_API_KEY=your_key
```

```python
import os
from piopiy.services.soniox.stt import SonioxSTTService

service = SonioxSTTService(api_key=os.getenv('SONIOX_API_KEY'))
```
