# Riva STT

```bash
pip install "piopiy-ai[riva]"
export RIVA_API_KEY=your_key
```

```python
import os
from piopiy.services.riva.stt import RivaSTTService

service = RivaSTTService(api_key=os.getenv('RIVA_API_KEY'))
```
