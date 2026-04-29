# Adding Custom / Open-Source Services

`VoiceAgent` accepts any service that implements the right base contract.
Cloud and open-source services are the same to the wrapper — what matters is
the base class you subclass and the abstract method you implement.

This guide covers the four kinds of services you can add, with copy-pasteable
templates. After implementing one, plug it into `voice_agent.configure()`
exactly like the bundled providers.

## Which base class do I subclass?

| Your model | Base class | Abstract method | Pipeline mode |
|---|---|---|---|
| Speech-to-text (audio in → text out) | `STTService` | `async def run_stt(audio)` | Cascaded |
| Text-only LLM (text in → text out) | `LLMService` | (uses chat-completion plumbing) | Cascaded |
| Audio-in LLM (audio in → text out) | `AIService` (custom `process_frame`) | n/a | Audio-LLM hybrid |
| Realtime / S2S (audio in → audio out) | `LLMService` (custom `process_frame`) | n/a | Speech-to-speech |
| Text-to-speech (text in → audio out) | `TTSService` | `async def run_tts(text)` | Cascaded / hybrid |

## 1. Custom STT

```python
from typing import AsyncGenerator
import asyncio

from piopiy.frames.frames import Frame, TranscriptionFrame, InterimTranscriptionFrame
from piopiy.services.stt_service import STTService
from piopiy.transcriptions.language import Language
from piopiy.utils.time import time_now_iso8601


class MyOpenSourceSTT(STTService):
    """STT that calls a local WebSocket server returning JSON transcripts."""

    def __init__(
        self,
        *,
        server_url: str,
        language: Language = Language.EN,
        sample_rate: int = 16000,
        **kwargs,
    ):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self._server_url = server_url
        self._language = language

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        # Send `audio` to your model server and emit transcription frames.
        # Pseudocode:
        text, is_final = await self._send_audio_and_recv(audio)
        if not text:
            return
        if is_final:
            yield TranscriptionFrame(text, self._user_id, time_now_iso8601(), language=self._language)
        else:
            yield InterimTranscriptionFrame(text, self._user_id, time_now_iso8601(), language=self._language)

    async def _send_audio_and_recv(self, audio: bytes) -> tuple[str, bool]:
        # Your protocol-specific implementation.
        await asyncio.sleep(0)  # placeholder
        return "", False
```

**Use it:**

```python
stt = MyOpenSourceSTT(server_url="ws://localhost:8765")
await voice_agent.configure(stt=stt, llm=..., tts=...)
```

## 2. Custom TTS

```python
from typing import AsyncGenerator

from piopiy.frames.frames import (
    Frame,
    TTSStartedFrame,
    TTSAudioRawFrame,
    TTSStoppedFrame,
)
from piopiy.services.tts_service import TTSService


class MyOpenSourceTTS(TTSService):
    """TTS that streams PCM audio chunks from a local server."""

    def __init__(
        self,
        *,
        server_url: str,
        voice: str = "default",
        sample_rate: int = 24000,
        **kwargs,
    ):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self._server_url = server_url
        self.set_voice(voice)

    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        yield TTSStartedFrame()
        try:
            async for pcm_chunk in self._stream_from_server(text):
                yield TTSAudioRawFrame(
                    audio=pcm_chunk,
                    sample_rate=self.sample_rate,
                    num_channels=1,
                )
        finally:
            yield TTSStoppedFrame()

    async def _stream_from_server(self, text: str):
        # Your protocol-specific implementation that yields raw PCM bytes.
        if False:
            yield b""
```

**Use it:**

```python
tts = MyOpenSourceTTS(server_url="ws://localhost:9000", voice="alice")
await voice_agent.configure(stt=..., llm=..., tts=tts)
```

For high-throughput TTS over a persistent socket, use `InterruptibleTTSService`
instead of the plain `TTSService` base — it adds reconnection, cancellation, and
back-pressure handling. See
[`ChatterboxTTSService`](../src/piopiy/services/opensource/chatterbox/tts.py)
as a working reference.

## 3. Custom audio-in LLM (Ultravox-style)

For models that take audio directly and emit text (no separate STT, but you
still need an external TTS), subclass `AIService` and consume audio frames in
`process_frame`. The pipeline runs in **audio-LLM hybrid** mode:
`input → llm → tts → output`.

```python
import asyncio
from typing import List, Optional

from piopiy.frames.frames import (
    AudioRawFrame,
    Frame,
    LLMFullResponseStartFrame,
    LLMFullResponseEndFrame,
    LLMTextFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.ai_service import AIService


class MyAudioLLM(AIService):
    """Buffers user audio between speech events, sends it to the model,
    and streams text frames back. Downstream TTS speaks the text."""

    def __init__(self, *, server_url: str, system_prompt: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._server_url = server_url
        self._system_prompt = system_prompt
        self._buffer: List[AudioRawFrame] = []
        self._speaking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStartedSpeakingFrame):
            self._buffer = []
            self._speaking = True

        elif isinstance(frame, AudioRawFrame) and self._speaking:
            self._buffer.append(frame)

        elif isinstance(frame, UserStoppedSpeakingFrame):
            self._speaking = False
            audio_bytes = b"".join(f.audio for f in self._buffer)
            await self._stream_response(audio_bytes)

        else:
            # Pass everything else through.
            await self.push_frame(frame, direction)

    async def _stream_response(self, audio: bytes):
        await self.push_frame(LLMFullResponseStartFrame())
        try:
            async for text_chunk in self._call_model(audio):
                await self.push_frame(LLMTextFrame(text_chunk))
        finally:
            await self.push_frame(LLMFullResponseEndFrame())

    async def _call_model(self, audio: bytes):
        # Your protocol-specific implementation that yields text chunks.
        if False:
            yield ""
```

**Use it:**

```python
llm = MyAudioLLM(server_url="ws://localhost:8766", system_prompt="You are helpful.")
tts = MyOpenSourceTTS(server_url="ws://localhost:9000")
await voice_agent.configure(llm=llm, tts=tts)   # no `stt=` → audio-LLM hybrid
```

See [`UltravoxService`](../src/piopiy/services/opensource/ultravox/omni.py) for
a complete production-grade implementation including reconnection, ping-pong,
and concurrent request handling.

## 4. Custom realtime / speech-to-speech

For models that take audio in and emit audio out (Gemini Live, OpenAI Realtime
style), the pattern is the same as audio-LLM but you push audio output frames
instead of text:

```python
from piopiy.frames.frames import (
    AudioRawFrame,
    Frame,
    OutputAudioRawFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from piopiy.processors.frame_processor import FrameDirection
from piopiy.services.llm_service import LLMService


class MyRealtimeLLM(LLMService):
    """Audio-in, audio-out — puts the agent in pure speech-to-speech mode."""

    def __init__(self, *, server_url: str, **kwargs):
        super().__init__(**kwargs)
        self._server_url = server_url
        self._session = None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, AudioRawFrame):
            await self._send_audio(frame.audio)
        else:
            await self.push_frame(frame, direction)

    async def _send_audio(self, audio: bytes):
        # Send to model; receive audio chunks back; push as OutputAudioRawFrame
        async for pcm in self._recv_audio():
            await self.push_frame(
                OutputAudioRawFrame(audio=pcm, sample_rate=24000, num_channels=1)
            )

    async def _recv_audio(self):
        if False:
            yield b""
```

**Use it:**

```python
llm = MyRealtimeLLM(server_url="wss://my-realtime-server")
await voice_agent.configure(llm=llm)   # no stt, no tts → speech-to-speech mode
```

## Function calling on a custom LLM

If your custom LLM supports tool calls and you want them to flow through
`voice_agent.add_tool(...)`, expose either `register_function(name, handler)`
or `register_tool(name, handler)` on your service. `VoiceAgent._build_task`
detects whichever you implement and routes registered handlers to it
automatically.

Cloud `LLMService` implementations already do this — see
[`OpenAILLMService`](../src/piopiy/services/openai/llm.py) for the canonical
shape.

## Testing your service in isolation

You don't need a phone call to validate a custom service. Wrap it in a
minimal pipeline with `LocalAudioTransport`:

```python
from piopiy.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams
from piopiy.pipeline.pipeline import Pipeline
from piopiy.pipeline.runner import PipelineRunner
from piopiy.pipeline.task import PipelineTask, PipelineParams

transport = LocalAudioTransport(LocalAudioTransportParams(audio_in_enabled=True, audio_out_enabled=True))
pipeline = Pipeline([transport.input(), my_service, transport.output()])
task = PipelineTask(pipeline, params=PipelineParams())
await PipelineRunner().run(task)
```

This loops your laptop's mic and speakers through the service, no telephony
required. Once it works locally, drop the same service into
`voice_agent.configure(...)` and it will run over the phone.

## Common pitfalls

1. **Sample rate mismatch.** TTS services must declare their output sample
   rate via `super().__init__(sample_rate=...)`. STT services receive audio
   at whatever rate the transport publishes (16 kHz by default for TeleCMI).
2. **Forgetting to call `super().process_frame(...)`.** All frame processors
   must call the parent's `process_frame` first or system frames (start/stop,
   interruptions) won't propagate.
3. **Pushing frames from the wrong direction.** Output frames
   (`TTSAudioRawFrame`, `OutputAudioRawFrame`) push downstream
   (`FrameDirection.DOWNSTREAM` is the default for `push_frame`). Don't
   override `direction` unless you know why.
4. **Holding state across calls.** `VoiceAgent` creates a fresh service in
   each `create_session` (assuming you instantiate inside the callback).
   Don't store call-scoped state on a module-level singleton.

## See also

- [Open-source examples](../example/opensource/) — complete runnable stacks
- [API Reference](API_REFERENCE.md) — full `configure()` parameter list
- [Migration Guide](MIGRATION.md) — moving from `Action()`/`SpeechAgent`
