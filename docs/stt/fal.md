# Fal STT

```bash
pip install "piopiy-ai[fal]"
export FAL_API_KEY=your_key
```

```python
import os
from piopiy.services.fal.stt import FalSTTService

service = FalSTTService(api_key=os.getenv('FAL_API_KEY'))
```
