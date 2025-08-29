# Neuphonic TTS

```bash
pip install "piopiy-ai[neuphonic]"
export NEUPHONIC_API_KEY=your_key
```

```python
import os
from piopiy.services.neuphonic.tts import NeuphonicTTSService

service = NeuphonicTTSService(api_key=os.getenv('NEUPHONIC_API_KEY'))
```
