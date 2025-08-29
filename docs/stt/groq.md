# Groq STT

```bash
pip install "piopiy-ai[groq]"
export GROQ_API_KEY=your_key
```

```python
import os
from piopiy.services.groq.stt import GroqSTTService

service = GroqSTTService(api_key=os.getenv('GROQ_API_KEY'))
```
