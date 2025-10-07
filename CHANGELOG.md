# Changelog

All notable changes to this project will be documented in this file.

## [1.1.1] - 2025-10-07

### Changed
- Model configuration field changed from dropdown to text input for flexibility
- Allows any OpenAI-compatible model name supported by bike4mind

## [1.1.0] - 2025-10-07

### Added
- Configurable LLM model selection via add-on GUI
- Support for multiple OpenAI models: gpt-4o-mini (default), gpt-4o, gpt-3.5-turbo, gpt-4
- Model dropdown selector in Configuration tab
- Voice assistant routing documentation with dynamic pipeline switching

### Changed
- Simplified README to show only HACS installation (removed manual installation)
- Removed standalone Docker installation option from documentation
- Model parameter now configurable instead of hardcoded

## [1.0.0] - 2025-10-06

### Added
- Initial release of bike4mind OpenAI Shim for Home Assistant
- OpenAI-compatible API endpoint for bike4mind integration
- Streaming and non-streaming response support
- Tool-calling support for Home Assistant device control
- Session management with TTL and turn limits
- Configurable timeouts and polling intervals
- Optional API key authentication
- Health check endpoint
- Comprehensive installation documentation
- Extended OpenAI Conversation integration guide
- Conversation routing examples with custom sentences and intents
