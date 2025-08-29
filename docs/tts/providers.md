# Text-to-Speech Providers

Quick start examples for every TTS provider supported by the library.

## AsyncAI

```bash
pip install "piopiy-ai[asyncai]"
export ASYNCAI_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.asyncai.tts import AsyncAITTSService

async def main():
    tts = AsyncAITTSService(api_key=os.getenv("ASYNCAI_API_KEY"))
    async for chunk in tts.stream("Hello from AsyncAI"):
        pass

asyncio.run(main())
```

## AWS

```bash
pip install "piopiy-ai[aws]"
export AWS_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.aws.tts import AWSPollyTTSService

async def main():
    tts = AWSPollyTTSService(api_key=os.getenv("AWS_API_KEY"))
    async for chunk in tts.stream("Hello from AWS"):
        pass

asyncio.run(main())
```

## Azure

```bash
pip install "piopiy-ai[azure]"
export AZURE_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.azure.tts import AzureBaseTTSService

async def main():
    tts = AzureBaseTTSService(api_key=os.getenv("AZURE_API_KEY"))
    async for chunk in tts.stream("Hello from Azure"):
        pass

asyncio.run(main())
```

## Cartesia

```bash
pip install "piopiy-ai[cartesia]"
export CARTESIA_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.cartesia.tts import CartesiaTTSService

async def main():
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"))
    async for chunk in tts.stream("Hello from Cartesia"):
        pass

asyncio.run(main())
```

## Deepgram

```bash
pip install "piopiy-ai[deepgram]"
export DEEPGRAM_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.deepgram.tts import DeepgramTTSService

async def main():
    tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    async for chunk in tts.stream("Hello from Deepgram"):
        pass

asyncio.run(main())
```

## ElevenLabs

```bash
pip install "piopiy-ai[elevenlabs]"
export ELEVENLABS_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

async def main():
    tts = ElevenLabsTTSService(api_key=os.getenv("ELEVENLABS_API_KEY"))
    async for chunk in tts.stream("Hello from ElevenLabs"):
        pass

asyncio.run(main())
```

## Fish

```bash
pip install "piopiy-ai[fish]"
export FISH_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.fish.tts import FishAudioTTSService

async def main():
    tts = FishAudioTTSService(api_key=os.getenv("FISH_API_KEY"))
    async for chunk in tts.stream("Hello from Fish"):
        pass

asyncio.run(main())
```

## Google

```bash
pip install "piopiy-ai[google]"
export GOOGLE_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.google.tts import GoogleHttpTTSService

async def main():
    tts = GoogleHttpTTSService(api_key=os.getenv("GOOGLE_API_KEY"))
    async for chunk in tts.stream("Hello from Google"):
        pass

asyncio.run(main())
```

## Groq

```bash
pip install "piopiy-ai[groq]"
export GROQ_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.groq.tts import GroqTTSService

async def main():
    tts = GroqTTSService(api_key=os.getenv("GROQ_API_KEY"))
    async for chunk in tts.stream("Hello from Groq"):
        pass

asyncio.run(main())
```

## Inworld

```bash
pip install "piopiy-ai[inworld]"
export INWORLD_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.inworld.tts import InworldTTSService

async def main():
    tts = InworldTTSService(api_key=os.getenv("INWORLD_API_KEY"))
    async for chunk in tts.stream("Hello from Inworld"):
        pass

asyncio.run(main())
```

## LMNT

```bash
pip install "piopiy-ai[lmnt]"
export LMNT_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.lmnt.tts import LmntTTSService

async def main():
    tts = LmntTTSService(api_key=os.getenv("LMNT_API_KEY"))
    async for chunk in tts.stream("Hello from LMNT"):
        pass

asyncio.run(main())
```

## MiniMax

```bash
pip install "piopiy-ai[minimax]"
export MINIMAX_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.minimax.tts import MiniMaxHttpTTSService

async def main():
    tts = MiniMaxHttpTTSService(api_key=os.getenv("MINIMAX_API_KEY"))
    async for chunk in tts.stream("Hello from MiniMax"):
        pass

asyncio.run(main())
```

## Neuphonic

```bash
pip install "piopiy-ai[neuphonic]"
export NEUPHONIC_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.neuphonic.tts import NeuphonicTTSService

async def main():
    tts = NeuphonicTTSService(api_key=os.getenv("NEUPHONIC_API_KEY"))
    async for chunk in tts.stream("Hello from Neuphonic"):
        pass

asyncio.run(main())
```

## OpenAI

```bash
pip install "piopiy-ai[openai]"
export OPENAI_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.openai.tts import OpenAITTSService

async def main():
    tts = OpenAITTSService(api_key=os.getenv("OPENAI_API_KEY"))
    async for chunk in tts.stream("Hello from OpenAI"):
        pass

asyncio.run(main())
```

## Piper

```bash
pip install "piopiy-ai[piper]"
export PIPER_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.piper.tts import PiperTTSService

async def main():
    tts = PiperTTSService(api_key=os.getenv("PIPER_API_KEY"))
    async for chunk in tts.stream("Hello from Piper"):
        pass

asyncio.run(main())
```

## PlayHT

```bash
pip install "piopiy-ai[playht]"
export PLAYHT_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.playht.tts import PlayHTTTSService

async def main():
    tts = PlayHTTTSService(api_key=os.getenv("PLAYHT_API_KEY"))
    async for chunk in tts.stream("Hello from PlayHT"):
        pass

asyncio.run(main())
```

## Rime

```bash
pip install "piopiy-ai[rime]"
export RIME_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.rime.tts import RimeTTSService

async def main():
    tts = RimeTTSService(api_key=os.getenv("RIME_API_KEY"))
    async for chunk in tts.stream("Hello from Rime"):
        pass

asyncio.run(main())
```

## Riva

```bash
pip install "piopiy-ai[riva]"
export RIVA_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.riva.tts import RivaTTSService

async def main():
    tts = RivaTTSService(api_key=os.getenv("RIVA_API_KEY"))
    async for chunk in tts.stream("Hello from Riva"):
        pass

asyncio.run(main())
```

## Sarvam

```bash
pip install "piopiy-ai[sarvam]"
export SARVAM_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.sarvam.tts import SarvamHttpTTSService

async def main():
    tts = SarvamHttpTTSService(api_key=os.getenv("SARVAM_API_KEY"))
    async for chunk in tts.stream("Hello from Sarvam"):
        pass

asyncio.run(main())
```

## XTTS

```bash
pip install "piopiy-ai[xtts]"
export XTTS_API_KEY=your_key
```

```python
import asyncio, os
from piopiy.services.xtts.tts import XTTSService

async def main():
    tts = XTTSService(api_key=os.getenv("XTTS_API_KEY"))
    async for chunk in tts.stream("Hello from XTTS"):
        pass

asyncio.run(main())
```

