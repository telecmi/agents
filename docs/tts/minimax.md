# Minimax TTS

```bash
pip install "piopiy-ai[minimax]"
export MINIMAX_API_KEY=your_key
```

```python
import os
from piopiy.services.minimax.tts import MiniMaxHttpTTSService

service = MiniMaxHttpTTSService(api_key=os.getenv('MINIMAX_API_KEY'))
```
