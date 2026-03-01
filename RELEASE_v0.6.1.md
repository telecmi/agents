CHANGELOG

## [0.6.1] - 2026-03-01

### Fixed
- Fixed various Python imports incorrectly referring to `pipecat` instead of `piopiy`.
- Updated PyProject configuration files to point to correct `piopiy` paths.
- Updated `VoiceAgent` internal processors to use universal `LLMContext` from `piopiy.processors.aggregators.llm_response_universal` in favor of deprecated `OpenAILLMContext`.
