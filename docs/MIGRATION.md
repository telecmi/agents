# Migration Guide

A cheat-sheet for moving existing Piopiy AI code to the unified `VoiceAgent.configure()` API.

> **Old code keeps working.** `voice_agent.Action(...)` and the
> `SpeechAgent` class are kept as deprecated aliases. Migration is optional
> but recommended for clarity.

## TL;DR

| Old | New |
|---|---|
| `voice_agent.Action(stt=, llm=, tts=)` | `voice_agent.configure(stt=, llm=, tts=)` |
| `SpeechAgent(...)` + `Action(omni=, tts=PassThroughTTS())` | `VoiceAgent(...)` + `configure(llm=)` |
| `SpeechAgent(...)` + `Action(omni=ultravox, tts=cartesia)` | `VoiceAgent(...)` + `configure(llm=ultravox, tts=cartesia)` |

## Three pipeline modes, one API

`VoiceAgent.configure()` auto-detects the mode from the arguments:

| Pass | Mode | Pipeline shape |
|------|------|----------------|
| `stt` + `llm` + `tts` | **Cascaded** | `input → stt → llm → tts → output` |
| `llm` only | **Speech-to-speech** | `input → llm → output` |
| `llm` + `tts` (no `stt`) | **Audio-LLM hybrid** | `input → llm → tts → output` |

## Cascaded code — almost no change

```python
# old (still works)
voice_agent = VoiceAgent(instructions=..., greeting=...)
await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
await voice_agent.start()

# new
voice_agent = VoiceAgent(instructions=..., greeting=...)
await voice_agent.configure(stt=stt, llm=llm, tts=tts, vad=True)
await voice_agent.start()
```

Only `Action` → `configure`. Same arguments, same behaviour.

## Speech-to-speech — drop the `PassThroughTTS` shim

If you were using `SpeechAgent` with a `PassThroughTTS` workaround:

```python
# old
from piopiy.speech_agent import SpeechAgent
from piopiy.processors.frame_processor import FrameProcessor, FrameDirection
from piopiy.frames.frames import Frame

class PassThroughTTS(FrameProcessor):
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)

agent = SpeechAgent(instructions=..., greeting=...)
await agent.Action(omni=gemini_live, tts=PassThroughTTS(), vad=True)
await agent.start()
```

becomes:

```python
# new — no shim, no SpeechAgent
from piopiy.voice_agent import VoiceAgent

voice_agent = VoiceAgent(instructions=..., greeting=...)
await voice_agent.configure(llm=gemini_live, vad=True)
await voice_agent.start()
```

The `PassThroughTTS` class can be deleted entirely.

## Audio-LLM hybrid (Ultravox, VibeVoice)

If your audio model emits text but you supply your own TTS:

```python
# old
agent = SpeechAgent(instructions=..., greeting=...)
await agent.Action(omni=ultravox, tts=cartesia, vad=vad)
await agent.start()

# new
voice_agent = VoiceAgent(instructions=..., greeting=...)
await voice_agent.configure(llm=ultravox, tts=cartesia, vad=vad)
await voice_agent.start()
```

`omni=` becomes `llm=`. That's the only required change.

## Imports

Most imports are unchanged. The only change worth making:

```diff
- from piopiy.speech_agent import SpeechAgent
+ from piopiy.voice_agent import VoiceAgent
```

`piopiy.speech_agent.SpeechAgent` still exists and works, but it now subclasses
`VoiceAgent`. New code can import directly from `piopiy.voice_agent`.

## Greeting behaviour

The `greeting` parameter on `VoiceAgent` works in all three modes; only the
delivery mechanism differs:

- **Cascaded** — the TTS service speaks the greeting verbatim via a
  `TTSSpeakFrame`.
- **Speech-to-speech / Hybrid** — the greeting is injected into the LLM
  context as a user instruction (`"Begin the call by saying exactly: …"`).
  The model paraphrases or repeats it, then waits for user input. If you need
  word-perfect greetings on a realtime model, phrase the instruction
  accordingly in your `instructions` string.

## VAD

`vad=` accepts the same values as before:

| Value | Behaviour |
|-------|-----------|
| `True` | Silero VAD with library defaults |
| `False` / `None` | No client-side VAD (server-side VAD on the model still applies for S2S) |
| `dict` | Custom params: `confidence`, `start_secs`, `stop_secs`, `min_volume` |
| `SileroVADAnalyzer(...)` | Fully pre-built analyzer |

For speech-to-speech models like Gemini Live, server-side VAD is on by default
and usually sufficient — you only need to pass `vad=` if you also want
client-side VAD.

## Tools / function calling

Unchanged:

```python
voice_agent.add_tool(schema, handler)
voice_agent.register_tool(name, handler)
```

The new `configure()` accepts an `mcp_tools=` argument for MCP integrations
(same as before).

## Backward-compat policy

- `voice_agent.Action(...)` — **alias of `configure()`**, kept indefinitely
  for now. Will be deprecated in a future major release with prior notice.
- `SpeechAgent` class — **subclass of `VoiceAgent`**, kept indefinitely. The
  `Action(omni=, tts=...)` shape works; `tts=PassThroughTTS()` is silently
  dropped with a `DeprecationWarning`.
- All existing examples in this repo continue to run unchanged. The repo's
  own examples have been updated to the new API as the canonical reference.

## Troubleshooting

### "Cascaded mode requires `stt`" error

You passed `tts=` but not `stt=`. Either:
- Add an `stt=` for full cascaded mode, **or**
- Drop `tts=` for speech-to-speech, **or**
- Keep both and pass an audio-in `llm` (Ultravox, VibeVoice) — that's the hybrid.

### Greeting not spoken in S2S mode

Make sure `greeting` is set on the `VoiceAgent` constructor. The realtime
model receives it as a user instruction; some models obey it more literally
than others. For Gemini Live, putting strong wording in `instructions` helps.

### Old `omni=` argument still passed

If you import `SpeechAgent` and call `Action(omni=...)`, it still works (the
shim forwards `omni` to `llm`). To migrate cleanly, switch to `VoiceAgent` and
use `configure(llm=...)`.

## Need help?

- [Examples](../example/) — every supported pattern has a working sample
- [API Reference](API_REFERENCE.md) — full `configure()` parameter list
- [Developer Guide](DEVELOPER_GUIDE.md) — concepts and best practices
- support@piopiy.com
