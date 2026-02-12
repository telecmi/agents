# Telephony Setup & Deployment

This guide covers setting up phone numbers, deploying your agent to production, and managing calls.

## Table of Contents

1. [Dashboard Setup](#dashboard-setup)
2. [Phone Number Configuration](#phone-number-configuration)
3. [Agent Deployment](#agent-deployment)
4. [Call Routing](#call-routing)
5. [Monitoring & Analytics](#monitoring--analytics)
6. [Production Best Practices](#production-best-practices)

---

## Dashboard Setup

### Create Your Account

1. Go to [dashboard.piopiy.com](https://dashboard.piopiy.com)
2. Sign up with your email
3. Verify your email address
4. Complete your profile

### Create a Voice AI Agent

1. Navigate to **Voice AI Agents** in the dashboard
2. Click **Create Agent**
3. Fill in agent details:
   - **Name**: Descriptive name (e.g., "Customer Support Agent")
   - **Description**: Purpose of the agent
4. Click **Create**
5. **Copy your credentials**:
   - `AGENT_ID`: Unique identifier
   - `AGENT_TOKEN`: Authentication token

⚠️ **Keep your `AGENT_TOKEN` secure!** Never commit it to version control.

---

## Phone Number Configuration

### Purchase a Phone Number

1. Go to **Phone Numbers** in the dashboard
2. Click **Buy Number**
3. Select your country and area code
4. Choose a number from available options
5. Complete the purchase

### Assign Number to Agent

1. Go to **Phone Numbers**
2. Click on your purchased number
3. Under **Configuration**, select:
   - **Type**: Voice AI Agent
   - **Agent**: Select your agent from dropdown
4. Click **Save**

Now calls to this number will route to your agent!

---

## Agent Deployment

### Development Environment

Run your agent locally for testing:

```bash
# Set environment variables
export AGENT_ID=your_agent_id
export AGENT_TOKEN=your_agent_token
export OPENAI_API_KEY=your_openai_key
export DEEPGRAM_API_KEY=your_deepgram_key
export CARTESIA_API_KEY=your_cartesia_key

# Run agent
python my_agent.py
```

### Production Deployment

#### Option 1: Cloud Server (Recommended)

Deploy to a cloud server (AWS, GCP, Azure, DigitalOcean):

**1. Prepare your server:**

```bash
# Install Python 3.10+
sudo apt update
sudo apt install python3.10 python3-pip

# Clone your agent code
git clone https://github.com/your-repo/your-agent.git
cd your-agent

# Install dependencies
pip install -r requirements.txt
```

**2. Set environment variables:**

```bash
# Create .env file
cat > .env << EOF
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key
AGENT_DEBUG=false
EOF
```

**3. Run as a service (systemd):**

```bash
# Create service file
sudo nano /etc/systemd/system/piopiy-agent.service
```

```ini
[Unit]
Description=Piopiy Voice AI Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/your-agent
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
EnvironmentFile=/home/ubuntu/your-agent/.env
ExecStart=/usr/bin/python3 my_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable piopiy-agent
sudo systemctl start piopiy-agent

# Check status
sudo systemctl status piopiy-agent

# View logs
sudo journalctl -u piopiy-agent -f
```

#### Option 2: Docker

**Dockerfile:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "my_agent.py"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  agent:
    build: .
    env_file:
      - .env
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Deploy:**

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Option 3: Kubernetes

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: piopiy-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: piopiy-agent
  template:
    metadata:
      labels:
        app: piopiy-agent
    spec:
      containers:
      - name: agent
        image: your-registry/piopiy-agent:latest
        env:
        - name: AGENT_ID
          valueFrom:
            secretKeyRef:
              name: piopiy-secrets
              key: agent-id
        - name: AGENT_TOKEN
          valueFrom:
            secretKeyRef:
              name: piopiy-secrets
              key: agent-token
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## Call Routing

### Basic Routing

All calls to your assigned number route to your agent automatically.

### Advanced Routing with Metadata

Pass custom data to your agent based on call source:

**1. Via Dashboard:**

When creating a test call, add metadata in JSON format:

```json
{
  "customer_id": "CUST_1001",
  "campaign": "summer_sale",
  "priority": 5
}
```

**2. Via API:**

```bash
curl -X POST https://api.piopiy.com/v1/calls \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "agent_id": "your_agent_id",
    "metadata": {
      "customer_id": "CUST_1001",
      "source": "website"
    }
  }'
```

**3. Handle in your agent:**

```python
async def create_session(call_id, metadata=None, **kwargs):
    if metadata:
        customer_id = metadata.get("customer_id")
        priority = metadata.get("priority", 1)
        
        # Route to specialized agent
        if priority > 5:
            voice_agent = VoiceAgent(
                instructions="You are a priority support agent...",
                greeting="Hello valued customer!"
            )
        else:
            voice_agent = VoiceAgent(
                instructions="You are a support agent...",
                greeting="Hello! How can I help?"
            )
```

---

## Monitoring & Analytics

### Call Logs

View call history in the dashboard:

1. Go to **Call Logs**
2. Filter by:
   - Date range
   - Agent
   - Phone number
   - Call status

### Call Details

Click on any call to see:
- Duration
- Caller/Called numbers
- Metadata
- Recording (if enabled)
- Transcription

### Application Logs

Monitor your agent's logs:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

async def create_session(call_id, **kwargs):
    logging.info(f"Call started: {call_id}")
    try:
        # Agent logic
        await voice_agent.start()
        logging.info(f"Call completed: {call_id}")
    except Exception as e:
        logging.error(f"Call failed: {call_id}, Error: {e}")
```

### Metrics to Track

- **Call Volume**: Total calls per day/hour
- **Call Duration**: Average call length
- **Success Rate**: Completed vs failed calls
- **Response Time**: Time to first response
- **Provider Costs**: Track API usage

---

## Production Best Practices

### 1. High Availability

Run multiple agent instances:

```python
# Use process manager (PM2, systemd, etc.)
# Or container orchestration (Kubernetes, ECS)
```

### 2. Error Handling

Implement comprehensive error handling:

```python
async def create_session(call_id, **kwargs):
    try:
        voice_agent = VoiceAgent(...)
        await voice_agent.start()
    except Exception as e:
        logging.error(f"Call {call_id} error: {e}")
        # Send alert to monitoring service
        # Play fallback message to caller
```

### 3. Rate Limiting

Protect against API rate limits:

```python
import asyncio
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    async def acquire(self):
        now = time()
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            await asyncio.sleep(sleep_time)
        
        self.calls.append(time())

# Use in agent
limiter = RateLimiter(max_calls=10, period=60)  # 10 calls per minute

async def create_session(call_id, **kwargs):
    await limiter.acquire()
    # Proceed with call
```

### 4. Secret Management

Never hardcode secrets:

```python
# ❌ Bad
api_key = "sk-1234567890"

# ✅ Good
import os
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Better (use secret manager)
from aws_secretsmanager import get_secret
api_key = get_secret("openai_api_key")
```

### 5. Health Checks

Implement health check endpoint:

```python
from aiohttp import web

async def health_check(request):
    return web.json_response({"status": "healthy"})

app = web.Application()
app.router.add_get('/health', health_check)

# Run alongside your agent
web.run_app(app, port=8080)
```

### 6. Graceful Shutdown

Handle shutdown signals:

```python
import signal
import asyncio

async def shutdown(agent):
    print("Shutting down gracefully...")
    await agent.shutdown()
    print("Shutdown complete")

async def main():
    agent = Agent(...)
    
    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown(agent))
        )
    
    await agent.connect()
```

### 7. Cost Optimization

Monitor and optimize costs:

```python
# Use cost-effective models
llm = OpenAILLMService(model="gpt-4o-mini")  # Cheaper than GPT-4

# Cache common responses
from functools import lru_cache

@lru_cache(maxsize=100)
def get_faq_response(question):
    # Return cached response for common questions
    pass

# Implement timeout for long calls
async def create_session(call_id, **kwargs):
    try:
        await asyncio.wait_for(voice_agent.start(), timeout=300)  # 5 min max
    except asyncio.TimeoutError:
        logging.warning(f"Call {call_id} exceeded timeout")
```

---

## Troubleshooting

### Agent Not Receiving Calls

1. Verify agent is running: `systemctl status piopiy-agent`
2. Check network connectivity
3. Verify `AGENT_ID` and `AGENT_TOKEN` are correct
4. Check dashboard for agent status

### Poor Call Quality

1. Check internet bandwidth (minimum 1 Mbps)
2. Reduce latency by choosing nearby providers
3. Enable `debug=True` to identify bottlenecks

### High Costs

1. Use cost-effective models (GPT-4o-mini vs GPT-4)
2. Implement caching for common responses
3. Set max call duration limits
4. Monitor provider usage in dashboards

---

## Next Steps

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Advanced features
- **[API Reference](API_REFERENCE.md)** - Complete API docs
- **[Examples](../example/README.md)** - Code examples

## Support

- **Email**: support@piopiy.com
- **Dashboard**: [dashboard.piopiy.com](https://dashboard.piopiy.com)
