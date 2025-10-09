# VISUAL_ASSIST Specification

## Overview

VISUAL_ASSIST is an optional feature for the bike4mind Home Assistant Add-on that provides visual feedback during voice assistant interactions by streaming animated GIFs to a web browser. This creates a more engaging user experience by showing different visual states (speaking vs. idle).

## Feature Description

When enabled, VISUAL_ASSIST will:
- Display GIF "A" (speaking animation) when the voice assistant is actively speaking
- Display GIF "B" (idle animation) when the voice assistant is idle/listening
- Serve these GIFs through an HTTP endpoint accessible from any web browser on the local network

## Use Cases

1. **Wall-mounted tablet display**: Show visual feedback next to voice assistant hardware
2. **Desktop companion**: Provide visual cues on a computer screen during voice interactions
3. **Smart home dashboard integration**: Embed assistant status into existing HA dashboards
4. **Accessibility**: Visual indicators for hearing-impaired users

## Configuration

### Add-on Configuration (config.yaml)

New optional configuration fields:

```yaml
options:
  # ... existing options ...
  visual_assist_enabled: false
  visual_assist_speaking_gif_url: ""
  visual_assist_idle_gif_url: ""

schema:
  # ... existing schema ...
  visual_assist_enabled: bool?
  visual_assist_speaking_gif_url: str?
  visual_assist_idle_gif_url: str?
```

### Configuration Parameters

- **visual_assist_enabled** (default: `false`): Enable/disable the VISUAL_ASSIST feature
- **visual_assist_speaking_gif_url**: Web URL (HTTP/HTTPS) to GIF displayed when speaking (required if visual_assist_enabled is true)
- **visual_assist_idle_gif_url**: Web URL (HTTP/HTTPS) to GIF displayed when idle (required if visual_assist_enabled is true)

### Configuration Validation

When `visual_assist_enabled` is `true`, both `visual_assist_speaking_gif_url` and `visual_assist_idle_gif_url` must be non-empty valid URLs.

## Architecture

### Component Overview

```
Web Browser Client
        ↓ (HTTP/WebSocket on port 3000)
    app.py (FastAPI - integrated server)
        ├── Existing: OpenAI Shim endpoints
        └── New: VISUAL_ASSIST endpoints (when enabled)
                ↓ (monitors internal state)
            bike4mind API activity tracking
```

### Implementation Approach

**Integrated Web Server**: VISUAL_ASSIST functionality will be integrated directly into the existing `app.py` FastAPI application. When enabled, additional routes and WebSocket endpoints are conditionally registered on the same port (3000) as the existing OpenAI shim.

### Implementation Components

#### 1. State Detection

The existing `app.py` tracks its own internal state:
- Set state to "speaking" when `/v1/chat/completions` request starts processing
- Track state during bike4mind quest creation and polling
- Return to "idle" when response is sent to client

**Why This Approach:**
- Direct knowledge of when bike4mind is processing (no external monitoring needed)
- Simpler implementation (no HA WebSocket API dependency)
- Accurate state tracking from the shim's perspective

#### 2. WebSocket Broadcasting

The FastAPI application broadcasts state changes to connected web clients:
- Maintains list of active WebSocket connections
- Broadcasts "speaking" or "idle" state changes to all connected clients
- Handles client connections, disconnections, and reconnections

#### 3. HTTP Endpoints

New routes added to existing FastAPI app (conditionally when VISUAL_ASSIST is enabled):

**Endpoints:**
- `GET /visual` - Serves HTML page with GIF viewer (embeds configured GIF URLs)
- `WebSocket /ws` - Real-time state updates for connected browsers
- `GET /visual/status` - Returns current assistant state (speaking/idle) and GIF URLs

#### 4. Web Client

A simple HTML/JavaScript page served at `/visual` that:
- Connects to WebSocket for real-time state updates
- Displays appropriate GIF based on current state
- Auto-reconnects on connection loss
- Uses vanilla JavaScript (no framework dependencies)

### State Machine

```
States:
- IDLE: Voice assistant is ready, not processing
- LISTENING: Voice assistant heard wake word, listening for command
- PROCESSING: Request sent to bike4mind, waiting for response
- SPEAKING: Text-to-speech is playing response
- ERROR: Error occurred in processing

Visual Mapping:
- IDLE → Display idle.gif
- LISTENING → Display idle.gif (or optionally a third "listening.gif")
- PROCESSING → Display speaking.gif
- SPEAKING → Display speaking.gif
- ERROR → Display idle.gif (or flash/error state)
```

## Technical Design

### File Structure

```
ha-b4m-addon/
├── app.py                    # Modified: Integrated VISUAL_ASSIST endpoints
├── run.sh                    # Modified: Export VISUAL_ASSIST environment variables
├── config.yaml               # Modified: Add visual_assist options
├── www/                      # New: Web client files
│   ├── index.html           # GIF viewer page
│   └── client.js            # WebSocket client logic
└── VISUAL_ASSIST.md         # This specification
```

**Physical Deployment:**
- Single Python process running `app.py`
- Listens on port 3000 for all endpoints (both shim and visual assist)
- GIF files loaded from user-provided web URLs (no local file serving required)
- Web client files bundled in add-on's `www/` directory

### Integration Points

#### app.py Modifications

**State Broadcasting:**
Add state tracking to the existing chat completion endpoint:

```python
# Notify connected clients when request starts
async def chat_completions(request: ChatCompletionRequest):
    if VISUAL_ASSIST_ENABLED:
        await broadcast_state("speaking")

    # ... existing quest creation and polling ...

    if VISUAL_ASSIST_ENABLED:
        await broadcast_state("idle")

    return response
```

**New Endpoints (conditionally registered):**
```python
if VISUAL_ASSIST_ENABLED:
    @app.get("/visual")
    async def visual_page():
        # Serve HTML viewer page with embedded GIF URLs

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        # Handle WebSocket connections and broadcasting

    @app.get("/visual/status")
    async def visual_status():
        # Return current state and configuration
```

#### run.sh Modifications

Export configuration as environment variables:

```bash
#!/usr/bin/with-contreturns

# Export VISUAL_ASSIST configuration
if bashio::config.true 'visual_assist_enabled'; then
    export VISUAL_ASSIST_ENABLED=true
    export VISUAL_ASSIST_SPEAKING_GIF_URL=$(bashio::config 'visual_assist_speaking_gif_url')
    export VISUAL_ASSIST_IDLE_GIF_URL=$(bashio::config 'visual_assist_idle_gif_url')

    # Validate URLs are non-empty
    if [ -z "$VISUAL_ASSIST_SPEAKING_GIF_URL" ] || [ -z "$VISUAL_ASSIST_IDLE_GIF_URL" ]; then
        echo "ERROR: visual_assist_enabled is true but GIF URLs are not configured"
        exit 1
    fi
fi

# Start single integrated app
python3 app.py
```

## API Specification

### WebSocket Protocol

**Connection:** `ws://YOUR_HA_IP:3000/ws`

**Message Format (Server → Client):**
```json
{
  "type": "state_change",
  "state": "speaking|idle",
  "timestamp": 1234567890
}
```

**Message Format (Client → Server):**
```json
{
  "type": "ping"
}
```

**Server Response:**
```json
{
  "type": "pong",
  "state": "idle"
}
```

### HTTP Endpoints

#### GET /visual
Returns HTML page with GIF viewer.

**Response:** `text/html`

#### GET /visual/status
Returns current assistant state and configuration.

**Response:**
```json
{
  "state": "idle|speaking",
  "visual_assist_enabled": true,
  "speaking_gif_url": "https://example.com/speaking.gif",
  "idle_gif_url": "https://example.com/idle.gif"
}
```

## Web Client Design

### HTML Structure

The HTML page will be generated dynamically by the `/visual` endpoint with GIF URLs embedded from configuration:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Voice Assistant Visual</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        #assistant-gif {
            max-width: 100%;
            max-height: 100vh;
            object-fit: contain;
        }
        .status {
            position: fixed;
            top: 10px;
            right: 10px;
            color: white;
            font-family: monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <img id="assistant-gif" src="{{ IDLE_GIF_URL }}" alt="Assistant">
    <div class="status">
        <span id="connection-status">Connecting...</span>
    </div>
    <script>
        // Embed GIF URLs from server configuration
        const SPEAKING_GIF_URL = "{{ SPEAKING_GIF_URL }}";
        const IDLE_GIF_URL = "{{ IDLE_GIF_URL }}";
    </script>
    <script src="/client.js"></script>
</body>
</html>
```

### JavaScript Client Logic

```javascript
// client.js
class VisualAssistClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 2000;
        this.gifElement = document.getElementById('assistant-gif');
        this.statusElement = document.getElementById('connection-status');
        this.connect();
    }

    connect() {
        const wsUrl = `ws://${window.location.host}/ws`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to Visual Assist');
            this.statusElement.textContent = 'Connected';
            this.statusElement.style.color = 'lime';
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'state_change') {
                this.updateGif(data.state);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.statusElement.textContent = 'Error';
            this.statusElement.style.color = 'red';
        };

        this.ws.onclose = () => {
            console.log('Disconnected, reconnecting...');
            this.statusElement.textContent = 'Reconnecting...';
            this.statusElement.style.color = 'yellow';
            setTimeout(() => this.connect(), this.reconnectInterval);
        };
    }

    updateGif(state) {
        const gifSrc = state === 'speaking' ? SPEAKING_GIF_URL : IDLE_GIF_URL;
        if (this.gifElement.src !== gifSrc) {
            this.gifElement.src = gifSrc + '?t=' + Date.now(); // Cache bust
        }
    }
}

// Initialize client
const client = new VisualAssistClient();
```

## State Detection Strategy

VISUAL_ASSIST monitors the bike4mind shim's internal API activity to track state:

**Implementation:**
- State set to "speaking" when `/v1/chat/completions` request received
- State maintained during bike4mind quest creation and polling
- State returns to "idle" when response is sent to client

**Rationale:**
- Direct knowledge of when bike4mind is actively processing
- No dependency on Home Assistant WebSocket API
- Simpler implementation with fewer moving parts
- Accurate from the shim's perspective (may not match TTS playback timing exactly)

**Error Handling:**
If a request fails (timeout, rate limit, API error), the state immediately returns to "idle" to reflect that processing has stopped.

**Future Enhancement:**
A hybrid approach could be implemented in later versions to monitor actual Home Assistant TTS playback state for more accurate "speaking" detection that matches when audio is actually playing.

## Security Considerations

1. **Network Access**: Visual assist web interface should only be accessible on LAN
2. **No Authentication Required**: Since it's read-only visual feedback, authentication may be optional
3. **Optional Authentication**: Could add same `shim_api_key` authentication if desired
4. **URL Validation**: Validate GIF URLs are well-formed HTTP/HTTPS URLs at startup
5. **CORS**: May need CORS headers if embedding in HA dashboard iframes
6. **External Resources**: Users are responsible for hosting GIFs on trusted servers (browser loads directly from configured URLs)

## Performance Considerations

1. **GIF File Size**: Recommend GIFs under 5MB for smooth loading (hosted on user's servers)
2. **WebSocket Overhead**: Minimal - only state changes broadcast
3. **Multiple Clients**: Support multiple browsers viewing simultaneously
4. **Resource Usage**: Lightweight - no file serving, only WebSocket broadcasting and HTML templating
5. **Network Dependencies**: GIF loading speed depends on user's hosting and browser's network connection

## Testing Plan

### Unit Tests
- State transitions work correctly
- WebSocket connections handle disconnects gracefully
- URL validation rejects invalid URLs
- Configuration validation fails when enabled without URLs

### Integration Tests
- State changes when chat completions occur
- Multiple clients receive simultaneous updates
- Auto-reconnect after service restart

### Manual Tests
1. Enable visual_assist in config
2. Access `http://YOUR_HA_IP:3000/visual` in browser
3. Say voice command to assistant
4. Verify GIF changes to speaking animation
5. Verify GIF returns to idle animation after response

## Future Enhancements

1. **Additional States**: Add separate GIFs for listening, processing, error states
2. **Customizable Transitions**: Fade effects between GIF changes
3. **Audio Sync**: Detect actual TTS playback for precise speaking state
4. **Dashboard Integration**: Create HA dashboard card component
5. **Multi-Assistant Support**: Track multiple voice satellites simultaneously
6. **Mobile App**: Native mobile app for visual feedback
7. **Configurable Layouts**: Different viewer layouts (fullscreen, corner, overlay)

## Migration Path

### Phase 1: Core Implementation (v1.2.0)
- Basic speaking/idle GIF switching
- WebSocket state broadcasting
- Simple web viewer
- Configuration options in add-on GUI

### Phase 2: Enhanced Detection (v1.3.0)
- Optional HA WebSocket integration for accurate TTS playback state
- Additional states (listening, error)
- Improved state detection accuracy

### Phase 3: Advanced Features (v1.4.0+)
- Dashboard card component
- Custom animations/effects
- Multi-assistant support

## Documentation Requirements

1. **README.md**: Add VISUAL_ASSIST section with setup instructions
2. **INSTALL.md**: Add optional step for configuring visual feedback
3. **CHANGELOG.md**: Document feature addition
4. **User Guide**: Create example GIFs and setup tutorial
5. **Troubleshooting**: Common issues (file paths, port conflicts, network access)

## Example GIF Recommendations

### Speaking GIF
- Animated character with moving mouth
- Pulsing or glowing effect
- Sound wave visualization
- Speech bubble animation

### Idle GIF
- Gentle breathing animation
- Blinking eyes
- Subtle color pulse
- Waiting/standby pose

**Sources for Hosting GIFs:**
- **Self-hosted**: Upload to Home Assistant's `/config/www/` directory, access via `http://YOUR_HA_IP:8123/local/your-gif.gif`
- **Cloud storage**: Upload to services like Imgur, GitHub, or Google Drive (with public sharing enabled)
- **CDN**: Use a CDN service for faster loading
- **Create custom**: Use tools like GIPHY, Canva, Adobe Express, or LottieFiles

**Example URLs:**
```
https://YOUR_HA_IP:8123/local/speaking.gif  (self-hosted in HA)
https://i.imgur.com/abc123.gif              (Imgur)
https://raw.githubusercontent.com/user/repo/main/speaking.gif  (GitHub)
```

## Dependencies

### Python Packages (additions to requirements.txt)
```
# FastAPI already supports WebSockets natively - no additional packages required
```

**Note**: FastAPI (already in requirements.txt) has built-in WebSocket support. No additional dependencies needed for VISUAL_ASSIST feature.

## Configuration Example

```yaml
# config.yaml
options:
  # Existing options...
  b4m_api_key: "your-api-key"
  ha_b4m_session_id: "your-session-id"
  b4m_user_id: "your-user-id"

  # New VISUAL_ASSIST options
  visual_assist_enabled: true
  visual_assist_speaking_gif_url: "https://YOUR_HA_IP:8123/local/speaking.gif"
  visual_assist_idle_gif_url: "https://YOUR_HA_IP:8123/local/idle.gif"
```

## Success Criteria

The VISUAL_ASSIST feature will be considered successful when:

1. ✅ Users can enable/disable feature via add-on configuration
2. ✅ Web browser displays idle GIF when assistant is ready
3. ✅ Web browser displays speaking GIF when assistant is processing/responding
4. ✅ State transitions occur within 500ms of actual state changes
5. ✅ Multiple clients can view simultaneously without performance degradation
6. ✅ Auto-reconnect works after network interruptions
7. ✅ Documentation is clear and includes troubleshooting guide
8. ✅ Feature does not impact existing shim functionality when disabled

## Design Decisions (Resolved)

1. **GIF Configuration**: ✅ Use web URLs (HTTP/HTTPS) instead of file paths
2. **State Timing**: ✅ Simple approach - "speaking" during request, "idle" when complete (not synced to TTS)
3. **Multiple Requests**: ✅ Not a priority for initial implementation
4. **WebSocket**: ✅ Broadcast to all connected clients
5. **Error Handling**: ✅ Return to "idle" on any error
6. **Default GIFs**: ✅ Users provide their own URLs (no bundled defaults)

## Open Questions

1. **HA Integration**: Should this be a separate HA integration vs. add-on feature?
2. **Customization**: Allow CSS customization via config file?
3. **Authentication**: Should `/visual` endpoint require authentication?

## References

- Home Assistant WebSocket API: https://developers.home-assistant.io/docs/api/websocket
- FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
- Home Assistant Add-on Development: https://developers.home-assistant.io/docs/add-ons
