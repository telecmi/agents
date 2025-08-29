# SambaNova STT

```bash
pip install "piopiy-ai[sambanova]"
export SAMBANOVA_API_KEY=your_key
```

```python
import os
from piopiy.services.sambanova.stt import SambaNovaSTTService

service = SambaNovaSTTService(api_key=os.getenv('SAMBANOVA_API_KEY'))
```
