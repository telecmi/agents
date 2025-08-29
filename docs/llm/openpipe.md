# OpenPipe LLM

```bash
pip install "piopiy-ai[openpipe]"
export OPENPIPE_API_KEY=your_key
```

```python
import os
from piopiy.services.openpipe.llm import OpenPipeLLMService

service = OpenPipeLLMService(api_key=os.getenv('OPENPIPE_API_KEY'))
```
