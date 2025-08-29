# Gladia STT

```bash
pip install "piopiy-ai[gladia]"
export GLADIA_API_KEY=your_key
```

```python
import os
from piopiy.services.gladia.stt import GladiaSTTService

service = GladiaSTTService(api_key=os.getenv('GLADIA_API_KEY'))
```
