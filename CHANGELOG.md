# Changelog

All notable changes to piopiy-ai will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2026-03-01

### Fixed
- Fixed various Python imports incorrectly referring to `pipecat` instead of `piopiy`.
- Updated PyProject configuration files to point to correct `piopiy` paths.
- Updated `VoiceAgent` internal processors to use universal `LLMContext` from `piopiy.processors.aggregators.llm_response_universal` in favor of deprecated `OpenAILLMContext`.

## [0.6.0] - 2026-02-12

### Added
- **40+ Provider Examples**: Comprehensive examples for all major AI providers
  - 8 STT providers: Deepgram, AssemblyAI, Azure, Google, Gladia, Speechmatics, OpenAI Whisper, Local Whisper
  - 13 LLM providers: OpenAI, Anthropic, Groq, Gemini, Mistral, Together AI, Fireworks, Ollama, Perplexity, DeepSeek, Cerebras, OpenRouter
  - 17 TTS providers: Cartesia, ElevenLabs, PlayHT, LMNT, Deepgram Aura, Azure, Google, OpenAI, Rime, Neuphonic, Fish Audio, Gradium, Hume AI, Speechmatics, Groq, Murf.ai
  - 2 optimized combined stacks (ultra-low latency, premium quality)
- **Complete Parameter Documentation**: New `docs/PARAMETERS.md` with comprehensive reference for all configuration options
- **Enhanced Examples**: All examples now include detailed parameter documentation and inline comments
- **Provider-Specific READMEs**: Dedicated documentation for STT, LLM, and TTS providers with comparison tables
- **Metadata Support**: Full documentation and examples showing how to use the metadata parameter for call customization
- **Organized Example Structure**: Examples organized into folders (basic/, mcp_sales/, murf/, providers/)

### Changed
- **Updated to Pipecat v0.0.99**: Synced all provider dependencies with latest Pipecat version
- **Enhanced Basic Example**: Now includes comprehensive parameter documentation with type hints and inline explanations
- **Improved README**: Updated with better examples and provider showcase
- **Package Branding**: Corrected package references from `pipecat-ai` to `piopiy-ai` throughout codebase

### Fixed
- Corrected package name references in error messages
- Fixed import statements in all examples
- Updated smart-turn model path to v3.2

### Documentation
- Added `docs/PARAMETERS.md` - Complete parameter reference
- Added `docs/DEVELOPER_GUIDE.md` - Comprehensive developer guide
- Added `docs/API_REFERENCE.md` - Full API documentation
- Added `docs/GETTING_STARTED.md` - Quick start guide
- Enhanced `example/README.md` with provider matrix
- Created provider-specific READMEs for STT, LLM, and TTS

## [0.5.1] - Previous Release

Initial release with core functionality.

---

[0.6.1]: https://github.com/telecmi/agents/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/telecmi/agents/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/telecmi/agents/releases/tag/v0.5.1
