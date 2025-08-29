# Cartesia STT

```bash
pip install "piopiy-ai[cartesia]"
export CARTESIA_API_KEY=your_key
```

```python
import os
from piopiy.services.cartesia.stt import CartesiaSTTService

service = CartesiaSTTService(api_key=os.getenv('CARTESIA_API_KEY'))
```
