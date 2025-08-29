# Azure STT

```bash
pip install "piopiy-ai[azure]"
export AZURE_API_KEY=your_key
```

```python
import os
from piopiy.services.azure.stt import AzureSTTService

service = AzureSTTService(api_key=os.getenv('AZURE_API_KEY'))
```
