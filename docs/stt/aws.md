# AWS STT

```bash
pip install "piopiy-ai[aws]"
export AWS_API_KEY=your_key
```

```python
import os
from piopiy.services.aws.stt import AWSTranscribeSTTService

service = AWSTranscribeSTTService(api_key=os.getenv('AWS_API_KEY'))
```
