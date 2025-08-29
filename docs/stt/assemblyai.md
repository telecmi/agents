# AssemblyAI STT

```bash
pip install "piopiy-ai[assemblyai]"
export ASSEMBLYAI_API_KEY=your_key
```

```python
import os
from piopiy.services.assemblyai.stt import AssemblyAISTTService

service = AssemblyAISTTService(api_key=os.getenv('ASSEMBLYAI_API_KEY'))
```
