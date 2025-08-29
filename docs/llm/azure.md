# Azure LLM

```bash
pip install "piopiy-ai[azure]"
export AZURE_API_KEY=your_key
```

```python
import os
from piopiy.services.azure.llm import AzureLLMService

service = AzureLLMService(api_key=os.getenv('AZURE_API_KEY'))
```
