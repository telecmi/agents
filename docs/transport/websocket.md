# WebSocket Transport

```bash
pip install "piopiy-ai[websocket]"
```

```python
from piopiy.transports.network.websocket_client import (
    WebsocketClientTransport,
    WebsocketClientParams,
)

transport = WebsocketClientTransport(
    uri="wss://example.com",
    params=WebsocketClientParams(),
)
```
