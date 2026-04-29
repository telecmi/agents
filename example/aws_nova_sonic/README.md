# AWS Nova Sonic — Speech-to-Speech Agent

Speech-to-speech voice agent using Amazon Nova Sonic. The model takes user
audio in and emits agent audio out.

See [docs/REALTIME_MODELS.md](../../docs/REALTIME_MODELS.md#4-aws-nova-sonic)
for the full constructor reference.

## Install

```bash
pip install "piopiy-ai[aws-nova-sonic,silero]" python-dotenv
```

> Requires Python 3.12+ (the AWS SDK Bedrock runtime dependency is 3.12-only).

## Supported regions

- **Nova 2 Sonic** (default): `us-east-1`, `us-west-2`, `ap-northeast-1`
- **Nova Sonic** (older): `us-east-1`, `ap-northeast-1`

## Environment

```bash
AGENT_ID=...
AGENT_TOKEN=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

## Run

```bash
python example/aws_nova_sonic/nova_sonic_agent.py
```

## Voices

`matthew` (default), plus the voices in the
[Nova voice docs](https://docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-language-support.html).
Some voices are tuned for specific languages.

## IAM permissions

Your AWS credentials need access to the Nova Sonic model in Bedrock. Minimum:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModelWithBidirectionalStream"],
    "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-2-sonic-v1:0"
  }]
}
```

## Other realtime models

- [Gemini Live](../gemini_live/), [OpenAI Realtime](../openai_realtime/),
  [Azure OpenAI Realtime](../azure_realtime/), [Grok Realtime](../grok_realtime/)
