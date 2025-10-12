# bike4mind OpenAI Shim for Home Assistant

OpenAI-compatible API shim that translates between Home Assistant's Extended OpenAI Conversation integration and bike4mind's quest-based polling API.

## Features

- ✅ OpenAI Chat Completion API compatibility
- ✅ Streaming and non-streaming responses
- ✅ Tool-calling support for Home Assistant device control
- ✅ Session management with TTL and turn limits
- ✅ Configurable timeouts and polling intervals
- ✅ Optional API key authentication
- ✅ Home Assistant Add-on with UI configuration
- ✅ **EXTROVERT**: Proactive AI conversations triggered by automations
- ✅ **VISUAL_ASSIST**: Visual feedback with animated GIFs

## Architecture

This shim acts as a bridge between two incompatible APIs:

```
Home Assistant Extended OpenAI Conversation
        ↓ (OpenAI format)
    bike4mind Shim
        ↓ (bike4mind format)
    bike4mind API
```

### API Translation

| Feature | OpenAI API | bike4mind API | Shim Action |
|---------|------------|---------------|-------------|
| Protocol | Synchronous | Async quest + polling | Create quest, poll until done |
| Auth | `Authorization: Bearer` | `X-API-Key` | Translate headers |
| Response | Immediate `choices[]` | Poll for `replies[]` | Extract from multiple fields |
| Tool-calling | Native `tool_calls` | JSON in response | Parse and translate |

## Installation

### Prerequisites

**Extended OpenAI Conversation Integration** is required. Install it via HACS:

1. Install HACS if you don't have it: https://hacs.xyz/docs/setup/download
2. Go to **HACS → Integrations**
3. Click **⋮** menu → **Custom repositories**
4. Add repository: `https://github.com/jekalmin/extended_openai_conversation`
5. Category: Integration → Click **Add**
6. Search for "Extended OpenAI Conversation" and click **Download**
7. Restart Home Assistant

### Step 1: Install bike4mind Shim Add-on

1. **Add this repository** to Home Assistant:
   - Go to **Settings → Add-ons → Add-on Store → ⋮ (menu) → Repositories**
   - Add URL: `https://github.com/speedybits/ha-b4m-addon`
   - Click **Add**

2. **Install the add-on**:
   - Refresh the add-on store page
   - Find "bike4mind OpenAI Shim" in the add-on store
   - Click **Install**

3. **Configure** via add-on configuration tab:
   - `b4m_api_key`: Your bike4mind API key
   - `ha_b4m_session_id`: bike4mind session ID
   - `b4m_user_id`: bike4mind user ID
   - `shim_api_key` (optional but recommended): API key for shim authentication

4. **Start the add-on**:
   - Go to **Info** tab → Click **Start**
   - Check **Log** tab to verify: "Uvicorn running on http://0.0.0.0:3000"

## Configuration

### Required Settings

- **b4m_api_key**: bike4mind API key
- **ha_b4m_session_id**: bike4mind session ID (all users share this session)
- **b4m_user_id**: bike4mind user ID

### Optional Settings

- **shim_api_key**: API key for securing shim access (recommended)
- **b4m_model**: LLM model to use (default: `gpt-4o-mini`)
  - Examples: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`, `gpt-4`
  - Any OpenAI-compatible model name supported by bike4mind
- **session_ttl_sec**: Session timeout in seconds (default: 600 / 10 minutes)
- **max_turns**: Maximum conversation turns before reset (default: 20)
- **timeout_ms**: Total request timeout in milliseconds (default: 60000 / 60 seconds)
- **poll_interval_ms**: Initial polling interval (default: 1500 / 1.5 seconds)
- **poll_max_interval_ms**: Maximum polling interval after backoff (default: 5000 / 5 seconds)
- **b4m_base**: bike4mind API base URL (default: `https://app.bike4mind.com/api`)
- **ha_tool_function_name**: Home Assistant tool function name (default: `homeassistant.call_service`)

### VISUAL_ASSIST Settings (Optional)

Visual feedback feature that displays animated GIFs in a web browser based on assistant state. Shows different animations for thinking (processing), speaking (TTS playback), and idle (ready) states.

**Configuration Options:**
- **visual_assist_enabled**: Enable/disable visual feedback (default: `false`)
- **visual_assist_thinking_gif_url**: Web URL to GIF displayed when bike4mind is thinking/processing
- **visual_assist_speaking_gif_url**: Web URL to GIF displayed when TTS (Piper) is speaking
- **visual_assist_idle_gif_url**: Web URL to GIF displayed when assistant is idle/ready

#### Setup Steps

**1. Prepare GIF Files**

You need three animated GIF files:
- **Thinking GIF**: Shown when bike4mind processes your request (e.g., spinning gears, loading animation)
- **Speaking GIF**: Shown when TTS plays audio (e.g., animated mouth, sound waves)
- **Idle GIF**: Shown when ready/waiting (e.g., gentle breathing, blinking)

**2. Host Your GIFs**

Option A - Self-hosted in Home Assistant (recommended):
1. Upload GIFs to `/config/www/` directory in Home Assistant
2. Access via: `http://YOUR_HA_IP:8123/local/filename.gif`
3. Example paths:
   - `/config/www/thinking.gif` → `http://192.168.1.100:8123/local/thinking.gif`
   - `/config/www/speaking.gif` → `http://192.168.1.100:8123/local/speaking.gif`
   - `/config/www/idle.gif` → `http://192.168.1.100:8123/local/idle.gif`

Option B - Cloud hosting:
- Upload to Imgur, GitHub, or similar service
- Get public sharing URLs

**3. Configure the Add-on**

Go to bike4mind add-on **Configuration** tab:

```yaml
visual_assist_enabled: true
visual_assist_thinking_gif_url: "http://YOUR_HA_IP:8123/local/thinking.gif"
visual_assist_speaking_gif_url: "http://YOUR_HA_IP:8123/local/speaking.gif"
visual_assist_idle_gif_url: "http://YOUR_HA_IP:8123/local/idle.gif"
```

Replace `YOUR_HA_IP` with your Home Assistant IP address.

**4. Restart the Add-on**

Go to **Info** tab → Click **Restart**

**5. Access the Visual Viewer**

Open a web browser and navigate to:
```
http://YOUR_HA_IP:3000/visual
```

You should see your idle GIF displayed with a "Connected" status in the top-right corner.

**6. Test It**

Ask your voice assistant a question. Watch the GIF change:
- **Idle** → **Thinking** (bike4mind processing) → **Speaking** (TTS playback) → **Idle**

**Use Cases:**
- Wall-mounted tablet display next to voice assistant
- Desktop companion during conversations
- Visual indicator for hearing-impaired users
- Multiple viewers synchronized across different devices

For technical details, see [VISUAL_ASSIST.md](VISUAL_ASSIST.md)

### EXTROVERT Settings (Optional)

EXTROVERT allows Home Assistant automations to send prompts to bike4mind for AI processing, with responses spoken aloud through TTS. This creates a conversational smart home where the assistant can proactively start conversations based on events.

**Configuration Options:**
- **extrovert_enabled**: Enable/disable EXTROVERT feature (default: `false`)
- **extrovert_rate_limit**: Maximum requests per hour (default: `10`, range: 1-100)
- **extrovert_tts_entity_id**: TTS engine entity ID (default: `tts.piper`)
- **extrovert_tts_voice**: Voice name for TTS responses (optional, blank = use TTS service default)

#### Setup Steps

**1. Enable EXTROVERT**

Go to bike4mind add-on **Configuration** tab:

```yaml
extrovert_enabled: true
extrovert_rate_limit: 10
extrovert_tts_entity_id: "tts.piper"
extrovert_tts_voice: "en_US-lessac-medium"  # Optional
```

- Set `extrovert_tts_entity_id` to match your TTS engine (e.g., `tts.piper`, `tts.google_translate_say`)
- Set `extrovert_tts_voice` to a specific voice, or leave blank to use default

**Finding Your TTS Voice:**
1. Go to **Settings → Voice Assistants → Text-to-Speech**
2. Click on your TTS engine (e.g., Piper)
3. Copy the voice name (e.g., `en_US-lessac-medium`)

**2. Restart the Add-on**

Go to **Info** tab → Click **Restart**

Check **Log** tab for: `EXTROVERT enabled - Rate limit: 10 requests per hour`

**3. Create REST Command**

Add to Home Assistant's `configuration.yaml`:

```yaml
rest_command:
  extrovert_trigger:
    url: "http://YOUR_HA_IP:3000/v1/extrovert/trigger"
    method: POST
    headers:
      Authorization: "Bearer YOUR_SHIM_API_KEY"
      Content-Type: "application/json"
    payload: >
      {
        "prompt": "{{ prompt }}",
        "context": {{ context | tojson }},
        "tts_config": {
          "media_player": "{{ media_player }}"
        }
      }
```

Replace:
- `YOUR_HA_IP` with your Home Assistant IP address (from Step 1 in installation)
- `YOUR_SHIM_API_KEY` with the `shim_api_key` from add-on configuration (Step 3 in installation)

**Important:** After editing `configuration.yaml`, restart Home Assistant:
- Go to **Settings → System → Restart**

**4. Create Motion Detection Automation**

Example: Greet when someone enters the living room

**Using Home Assistant GUI:**

1. Go to **Settings → Automations & Scenes**
2. Click **Create Automation** (bottom right)
3. Click **Create new automation**
4. Add trigger:
   - **Trigger type**: State
   - **Entity**: `binary_sensor.living_room_motion` (your motion sensor)
   - **To**: `Detected`
5. Add condition (optional but recommended):
   - **Condition type**: Time
   - **After**: `18:00:00`
   - **Before**: `23:00:00`
6. Add action:
   - **Action type**: Call service
   - **Service**: `rest_command.extrovert_trigger`
   - **Action data**:
     ```yaml
     prompt: |
       Someone just entered the living room. Say a greeting in one sentence. It should be playful and friendly.
     context:
       trigger_type: motion_detected
       location: living_room
     tts_config:
       media_player: media_player.YOUR_SPEAKER_NAME
     ```
7. Replace `media_player.YOUR_SPEAKER_NAME` with your actual media player entity ID
8. Click **Save**
9. Name it: `EXTROVERT - Living Room Motion`

**Important Format Note:** The `media_player` must be inside `tts_config` as shown above. This structure is required by the EXTROVERT API.

**5. Test It**

Trigger motion in your living room. Within 5-30 seconds, you should hear bike4mind's response through your speaker.

#### More Automation Examples

**Temperature Alert:**
```yaml
prompt: |
  The bedroom temperature is {{ states('sensor.bedroom_temperature') }}°F. Comment on this in a lighthearted way in 1 sentence.
context:
  trigger_type: temperature_alert
  temperature: "{{ states('sensor.bedroom_temperature') }}"
tts_config:
  media_player: media_player.bedroom_speaker
```

**Door Open Welcome:**
```yaml
prompt: |
  The front door just opened at {{ now().strftime('%I:%M %p') }}. Welcome whoever arrived home in 1 sentence.
context:
  trigger_type: door_opened
  location: front_door
tts_config:
  media_player: media_player.living_room_speaker
```

**Device Status:**
```yaml
prompt: |
  The washing machine cycle just finished. Let me know in 1 sentence.
context:
  trigger_type: appliance_finished
  device: washing_machine
tts_config:
  media_player: media_player.kitchen_speaker
```

**Prompt Engineering Tips:**
- Ask for "1 sentence" to keep responses brief
- Include tone guidance ("friendly", "lighthearted", "motivational")
- Provide context about what happened
- Use specific instructions ("greet them", "welcome them home")
- Use Home Assistant templating for dynamic data (time, sensor values, etc.)

**Key Features:**
- Automation-triggered prompts sent to bike4mind
- Responses spoken via Home Assistant TTS
- Same session ID as interactive conversations (context continuity)
- Rate limiting to prevent spam (default: 10 requests/hour)
- Busy state management (one request at a time)
- Silent error handling (errors logged but not spoken)
- Integrates with VISUAL_ASSIST for visual feedback

**Important Limitation:**
After EXTROVERT speaks a response, the voice assistant does NOT automatically start listening. Users must say the wake word again to respond. This is a Home Assistant platform limitation. Best suited for one-way announcements or rhetorical questions.

For complete specification and advanced examples, see [EXTROVERT.md](EXTROVERT.md)

## Home Assistant Integration

### Step 2: Configure Extended OpenAI Conversation

After installing the add-on and Extended OpenAI Conversation:

1. **Find your Home Assistant IP**:
   - Go to **Settings → System → Network**
   - Note your IPv4 address (e.g., `192.168.68.111`)
   - **Test the shim is running** (from your computer's terminal):
     ```bash
     curl http://YOUR_HA_IP:3000/healthz
     ```
     Should return: `{"status":"healthy","service":"bike4mind-shim"}`

2. **Add Extended OpenAI Conversation integration**:
   - In Home Assistant, go to **Settings → Devices & Services**
   - Click **+ ADD INTEGRATION** (bottom right)
   - Search for "Extended OpenAI Conversation"
   - Click on it to start the setup wizard

3. **Fill in the configuration form** (you'll see these fields):

   **Name:**
   - Enter: `bike4mind` (or any name you prefer)

   **API Key:**
   - Enter the `shim_api_key` you set in the add-on configuration
   - If you didn't set one in the add-on, leave this blank

   **Base Url:**
   - ⚠️ **IMPORTANT**: Change this from `https://api.openai.com/v1` to your Home Assistant IP
   - Enter: `http://YOUR_HA_IP:3000/v1` (use YOUR actual HA IP from step 1)
   - Example: `http://192.168.68.111:3000/v1`
   - **Must include port 3000**
   - Do NOT use `localhost` or `127.0.0.1` (won't work)

   **Api Version:**
   - Leave blank (not needed)

   **Organization:**
   - Leave blank (not needed)

   **Skip Authentication:**
   - Leave unchecked

   Click **SUBMIT**

4. **Configure additional options**:
   - After submitting, the integration will appear in **Settings → Devices & Services**
   - Click **CONFIGURE** on the Extended OpenAI Conversation integration
   - In the options:
     - **Model**: Enter `bike4mind`
     - **Prompt Template**: Leave as default or customize
     - **Control Home Assistant**: ✅ Check this box (enables device control)
   - Click **SUBMIT**

5. **Verify the connection**:
   - The integration should show as active with no errors
   - If it shows an error, check:
     - Is the add-on running? (Check logs)
     - Is your IP address correct in Base Url?
     - Does your shim_api_key match in both places?

6. **Create bike4mind assistant**:
   - Go to **Settings → Voice Assistants → Assistants**
   - Click **Add Assistant**
   - **Name**: `bike4mind` (or your preferred name)
   - **Conversation Agent**: Select `bike4mind`
   - **Language**: Your preferred language
   - Click **Create**
   - **Keep your default assistant set to Home Assistant** (for normal use)
   - Manually switch to bike4mind assistant when you want to use it

## Testing

Test the integration using Home Assistant's Assist interface:

1. **Go to Settings → Voice Assistants → Assist**
2. **Switch to bike4mind**: Click the assistant dropdown and select `bike4mind`
3. **Ask questions or give commands**:
   - "What should I cook for dinner?" → Conversational AI response
   - "Turn on the kitchen light" → Device control via tool-calling
   - "Set living room to 50% brightness" → Multi-parameter device control
4. **Response time**: Expect 5-30 seconds for all queries (bike4mind processing)

**Note**: bike4mind handles both conversation AND device control, so no mode switching is needed.

## API Endpoints

### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint.

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "What should I cook for dinner?"}
  ],
  "model": "bike4mind",
  "stream": false
}
```

**Response**:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "bike4mind",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Based on what you have..."
    },
    "finish_reason": "stop"
  }]
}
```

### GET /healthz

Health check endpoint (no authentication required).

**Response**:
```json
{
  "status": "healthy",
  "service": "bike4mind-shim"
}
```

### POST /admin/reset_session

Reset internal session tracking (requires authentication).

**Request**:
```json
{
  "user_id": "default"
}
```

**Response**:
```json
{
  "status": "reset",
  "user_id": "default"
}
```

## Tool-Calling for Device Control

bike4mind can control Home Assistant devices by outputting structured JSON:

**bike4mind response format**:
````
Here's the action:
```json
{
  "action": "call_service",
  "domain": "light",
  "service": "turn_on",
  "entity_id": "light.kitchen",
  "data": {"brightness": 255}
}
```
````

**Translated to OpenAI tool_calls**:
```json
{
  "tool_calls": [{
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "homeassistant.call_service",
      "arguments": "{\"domain\":\"light\",\"service\":\"turn_on\",\"entity_id\":\"light.kitchen\",\"data\":{\"brightness\":255}}"
    }
  }]
}
```

Enable tool-calling in Extended OpenAI Conversation integration settings:
- ✅ **Control Home Assistant** enabled

## Testing

### Test Health Endpoint

```bash
curl http://YOUR_HA_IP:3000/healthz
```

### Test Chat Completion (No Auth)

```bash
curl -X POST http://YOUR_HA_IP:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "bike4mind",
    "stream": false
  }'
```

### Test Chat Completion (With Auth)

```bash
curl -X POST http://YOUR_HA_IP:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SHIM_API_KEY" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "bike4mind",
    "stream": false
  }'
```

## Troubleshooting

### "Unauthorized" Error

- Check that `SHIM_API_KEY` matches the API key in Extended OpenAI Conversation
- Verify the `Authorization: Bearer` header is correct

### "bike4mind credentials not configured"

- Ensure `B4M_API_KEY`, `B4M_SESSION_ID`, and `B4M_USER_ID` are set in add-on configuration
- Restart the add-on after configuration changes

### "bike4mind quest timeout"

- Check bike4mind API status
- Increase `timeout_ms` in configuration if queries are complex
- Check network connectivity between add-on and bike4mind API

### "Failed to connect" from Home Assistant

- Verify the Base URL uses your LAN IP (not `localhost`)
- Check that port 3000 is accessible: `curl http://YOUR_HA_IP:3000/healthz`
- Ensure add-on is running

### No Response from bike4mind

- Check add-on logs for errors
- Verify bike4mind session ID is valid
- Test bike4mind API directly with a tool like Postman

## Architecture Details

### Session Management

The shim maintains two types of sessions:

1. **Internal Shim Sessions**: Track conversation TTL and turn limits to prevent unbounded context growth
2. **bike4mind Session**: Single shared session (configured via `B4M_SESSION_ID`) used for all users

### Polling Strategy

- **Initial interval**: 1.5 seconds
- **Backoff**: Exponential up to 5 seconds maximum
- **Timeout**: 60 seconds total
- **Status checks**: `running` → continue polling, `done` → extract response, `stopped` → error

### Response Extraction Priority

1. `replies[]` array (join with newlines)
2. `reply` field
3. `questMasterReply` field
4. `researchModeResults[].response` (join with double newlines)

## Security Considerations

- ✅ Set `SHIM_API_KEY` to prevent unauthorized access
- ✅ Never expose shim to the internet (LAN only)
- ✅ bike4mind credentials stored in add-on config (not in code)
- ✅ Home Assistant handles all internet-facing authentication

## Performance

- **Typical response time**: 5-30 seconds (depends on bike4mind API and query complexity)
- **Health check**: <100ms
- **Local HA commands**: Unchanged (<100ms)

## Limitations

- Single shared bike4mind session (all household users share conversation context)
- No access to Home Assistant state/history (pure conversational AI)
- Requires internet connection for bike4mind API

## License

MIT

## Support

For issues and questions:
- GitHub Issues: [Your repository URL]
- Specification: See `HA_B4M_SPEC.md` in repository
