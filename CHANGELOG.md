# Changelog

All notable changes to this project will be documented in this file.

## [1.3.11] - 2025-10-12

### Fixed
- EXTROVERT TTS now uses `cache: true` for Home Assistant Cloud
- Cloud TTS requires cache enabled, not disabled or omitted
- Based on testing with Developer Tools showing cache must be checked

### Technical
- Cloud TTS engines: `cache: true`
- Other TTS engines (Piper, etc.): `cache: false`

## [1.3.10] - 2025-10-12

### Fixed
- EXTROVERT TTS compatibility with Home Assistant Cloud (`tts.cloud_say`)
- Removed `cache` parameter for cloud TTS engines (not supported)
- Cache parameter now only included for non-cloud TTS engines

### Technical
- Conditional cache parameter based on TTS entity ID detection
- Cloud TTS engines identified by "cloud" in entity_id string

## [1.3.9] - 2025-10-12

### Changed
- Expanded VISUAL_ASSIST documentation in README.md with complete setup guide
- Expanded EXTROVERT documentation in README.md with step-by-step instructions
- Added detailed motion detection automation example with correct `tts_config` format
- Added multiple automation examples (temperature, door, device status)
- Consolidated setup instructions from VISUAL_ASSIST.md and EXTROVERT.md into README.md
- README.md is now the primary user-facing documentation

### Documentation
- VISUAL_ASSIST section now includes GIF hosting options and complete setup steps
- EXTROVERT section now includes REST command setup and GUI-based automation creation
- Emphasized correct JSON structure: `tts_config: { media_player: ... }`
- Added prompt engineering tips and best practices

## [1.3.8] - 2025-10-12

### Added
- Custom exception handler for 422 validation errors
- Logs received request body and validation errors for debugging
- Returns detailed error response with validation error details

### Changed
- 422 errors now show what was received and why it failed

## [1.3.7] - 2025-10-12

### Changed
- Enhanced EXTROVERT TTS debug logging with comprehensive details
- Now logs: URL, TTS entity, media player, message preview, voice, full service data
- Success logging now shows ✅ instead of 🔊 for clarity
- Error logging shows sanitized auth token (last 8 chars only)
- Multi-line structured logging for easier reading

## [1.3.6] - 2025-10-12

### Added
- New configuration option: `extrovert_tts_entity_id` (default: `tts.piper`)
- Allows users to specify which TTS engine to use for EXTROVERT

### Fixed
- Made TTS engine configurable instead of hardcoded to `tts.piper`
- Now supports any TTS engine (Piper, Google Translate, Amazon Polly, etc.)

### Changed
- Added TTS entity logging to startup output

## [1.3.5] - 2025-10-12

### Fixed
- Corrected TTS service call format to use `entity_id: tts.piper` and `media_player_entity_id`
- Previously was incorrectly using `entity_id` for media player instead of TTS engine

### Technical
- `entity_id` now points to TTS engine (tts.piper)
- `media_player_entity_id` now points to media player device
- This matches Home Assistant's tts.speak service requirements

## [1.3.4] - 2025-10-12

### Fixed
- Added `cache: false` parameter to TTS service call
- Removed `language` parameter that was causing 400 errors

### Changed
- Enhanced debug logging to show request data and full response body
- Added pre-call logging to show TTS service data being sent

## [1.3.3] - 2025-10-12

### Fixed
- EXTROVERT TTS service data format to use `entity_id` and `language` parameters
- Enhanced error logging to show response text instead of JSON for better debugging

### Changed
- Added version number to startup log output

## [1.3.2] - 2025-10-12

### Fixed
- EXTROVERT TTS API call format to use correct `media_player_entity_id` parameter
- Enhanced error logging to show detailed error responses for TTS failures

## [1.3.1] - 2025-10-12

### Fixed
- EXTROVERT TTS authentication by adding `homeassistant_api: true` to config.yaml
- Add-on now receives SUPERVISOR_TOKEN required for calling tts.speak service

### Changed
- Improved INSTALL.md with GUI-focused instructions for automation creation (Step 12C)
- Clarified shim_api_key configuration in INSTALL.md (Step 12B)

## [1.3.0] - 2025-10-12

### Added
- EXTROVERT feature: Proactive AI conversations triggered by Home Assistant automations
- New API endpoint `/v1/extrovert/trigger` for automation-triggered prompts
- Configuration options: `extrovert_enabled`, `extrovert_rate_limit`, `extrovert_tts_voice`
- Rate limiting system (default: 10 requests per hour, configurable 1-100)
- Busy state management to prevent concurrent EXTROVERT requests
- Response sanitization for TTS (strips markdown, JSON blocks, truncates to 200 words)
- Silent error handling (errors logged but not spoken)
- VISUAL_ASSIST integration for EXTROVERT (thinking/speaking/idle states)
- Session continuity: EXTROVERT uses same session ID as interactive conversations
- Comprehensive documentation in EXTROVERT.md specification
- Installation guide in INSTALL.md (Step 12)
- REST command and automation examples

### Changed
- Updated README.md with EXTROVERT feature overview
- Enhanced startup logging to show EXTROVERT status

### Technical
- EXTROVERT prompts sent directly to bike4mind (no transformation)
- Uses `tts.speak` service with optional voice override
- TTS duration estimation for VISUAL_ASSIST state transitions
- Architecture supports conversation-focused prompts (not device control)

### Limitations Documented
- No automatic listening after TTS responses (Home Assistant platform limitation)
- Best suited for one-way announcements or rhetorical questions
- Users must say wake word again to respond to EXTROVERT prompts

## [1.2.2] - 2025-10-09

### Fixed
- TTS duration estimation now matches actual Piper speech rate
- Changed TTS estimation from 3.3 to 16 characters per second (4.8x faster)
- Reduced minimum speaking duration from 2 seconds to 1 second
- "Speaking" GIF now transitions to "Idle" when Piper actually finishes speaking

### Technical
- Based on measured Piper TTS rate: 113 chars in 7 seconds = ~16 chars/sec
- Previous rate (3.3 chars/sec) caused speaking GIF to remain 22+ seconds too long

## [1.2.1] - 2025-10-09

### Added
- Third visual state: "thinking" GIF displayed during bike4mind processing
- `visual_assist_thinking_gif_url` configuration parameter
- TTS duration estimation for automatic transition from speaking to idle
- Background task to return to idle state after estimated TTS playback

### Changed
- VISUAL_ASSIST now has three states: idle → thinking → speaking → idle
- State transitions:
  - "thinking" when request received and bike4mind is processing
  - "speaking" when response ready and TTS (Piper) is playing
  - "idle" when TTS completes or on error
- Updated WebSocket protocol to include "thinking" state
- Updated `/visual/status` endpoint to return thinking_gif_url

### Technical
- TTS duration estimated at ~3.3 characters per second (min 2s, max 30s)
- Background asyncio task handles automatic state transition to idle

## [1.2.0] - 2025-10-09

### Added
- VISUAL_ASSIST feature: Optional visual feedback via web browser
- Display animated GIFs based on assistant state (speaking/idle)
- WebSocket endpoint `/ws` for real-time state broadcasting
- Web viewer at `/visual` endpoint showing GIF animations
- Status endpoint `/visual/status` for current state and configuration
- Configuration options: `visual_assist_enabled`, `visual_assist_speaking_gif_url`, `visual_assist_idle_gif_url`
- Real-time state updates to all connected browser clients
- Auto-reconnect support for browser disconnections

### Changed
- Version bumped to 1.2.0
- Enhanced chat completions endpoint with state broadcasting
- Improved error handling returns to idle state

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
