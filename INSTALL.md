# Installation Guide: bike4mind Home Assistant Integration

Complete step-by-step guide to integrate bike4mind AI with Home Assistant.

## Prerequisites

- Home Assistant OS, Supervised, or Container installation
- bike4mind account with API access
- Extended OpenAI Conversation integration (installed from HACS or HA integrations)

## Step 1: Gather bike4mind Credentials

You'll need three pieces of information from bike4mind:

1. **API Key** (`B4M_API_KEY`)
2. **Session ID** (`HA_B4M_SESSION_ID`)
3. **User ID** (`B4M_USER_ID`)

**Finding your credentials**:
- API Key: bike4mind account settings or API dashboard
- Session ID: From bike4mind web app URL or API calls
- User ID: From bike4mind account profile

## Step 2: Install the bike4mind Shim Add-on

### Add the Repository

1. Open Home Assistant
2. Go to **Settings → Add-ons → Add-on Store**
3. Click **⋮ (menu)** in the top right
4. Select **Repositories**
5. Add this repository URL:
   ```
   https://github.com/YOUR_USERNAME/b4m_yahboom
   ```
6. Click **Add**

### Install the Add-on

1. Refresh the add-on store page
2. Find **bike4mind addon** in the list
3. Click on it
4. Click **Install**
5. Wait for installation to complete

## Step 3: Configure the Add-on

1. Click on the **Configuration** tab
2. Fill in the required fields:

```yaml
b4m_api_key: "YOUR_B4M_API_KEY_HERE"
ha_b4m_session_id: "YOUR_HA_B4M_SESSION_ID_HERE"
b4m_user_id: "YOUR_B4M_USER_ID_HERE"
shim_api_key: "create_a_secure_random_key"  # Generate with: openssl rand -hex 32
b4m_model: "gpt-4o-mini"  # Options: gpt-4o-mini, gpt-4o, gpt-3.5-turbo, gpt-4
```

3. Optionally adjust model and performance settings:
   - **b4m_model**: Select which LLM model to use (default: gpt-4o-mini)
   - Other performance settings can be left at defaults
4. Click **Save**

## Step 4: Start the Add-on

1. Go to the **Info** tab
2. Click **Start**
3. Enable **Start on boot** and **Watchdog** (recommended)
4. Check the **Log** tab for startup messages
5. Verify you see: `🚀 bike4mind addon started`

## Step 5: Find Your Home Assistant LAN IP

You need your HA instance's LAN IP address (not `localhost`).

**Method 1: Settings**
- Go to **Settings → System → Network**
- Note the IPv4 address (e.g., `192.168.1.100`)

**Method 2: SSH/Terminal**
```bash
hostname -I
```

**Method 3: Router**
- Check your router's DHCP client list for "homeassistant"

## Step 6: Test the Shim

Open a terminal and test the health endpoint:

```bash
curl http://YOUR_HA_IP:3000/healthz
```

Expected response:
```json
{"status":"healthy","service":"bike4mind-shim"}
```

## Step 7: Install Extended OpenAI Conversation

If not already installed:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **"Extended OpenAI Conversation"**
4. Click to install
5. If not found, install via HACS:
   - Go to HACS → Integrations
   - Search for "Extended OpenAI Conversation"
   - Install it
   - Restart Home Assistant

## Step 8: Configure Extended OpenAI Conversation

1. Go to **Settings → Devices & Services**
2. Find **Extended OpenAI Conversation**
3. Click **Configure**
4. Enter the following settings:

**Basic Settings:**
- **Name**: `bike4mind` (or any name you prefer)
- **API Base URL**: `http://YOUR_HA_IP:3000/v1`
  - Replace `YOUR_HA_IP` with your LAN IP from Step 5
  - Example: `http://192.168.1.100:3000/v1`
- **API Key**: The `shim_api_key` you set in Step 3
- **Model**: `bike4mind`

**Advanced Settings:**
- ✅ Enable **"Control Home Assistant"** (for device control via tool-calling)
- ❌ **Do NOT** set as default conversation agent

5. Click **Submit**

## Step 9: Create bike4mind Assistant

1. Go to **Settings → Voice Assistants → Assistants**
2. Click **Add Assistant**
3. Configure:
   - **Name**: `bike4mind` (or your preferred name like `Rosie`)
   - **Conversation Agent**: Select `bike4mind`
   - **Language**: Your preferred language
4. Click **Create**
5. **Keep your default assistant set to Home Assistant** (do not change preferred assistant)

## Step 10: Test the Integration

Test bike4mind using the built-in Assist chat:

1. **Go to Settings → Voice Assistants → Assist**
2. **Switch to bike4mind**: Click the assistant dropdown and select `bike4mind`
3. **Type or speak test queries**:
   - "What should I cook for dinner?" → Conversational AI response
   - "Turn on the kitchen light" → Device control via tool-calling
   - "Set living room to 50% brightness" → Multi-parameter control
4. **Expected behavior**:
   - 5-30 second response time for all queries
   - bike4mind handles both conversation AND device control
   - No mode switching needed

**Note**: To use bike4mind with voice, either manually switch the assistant dropdown before speaking, or configure your voice satellite to use the bike4mind assistant.

If successful, proceed to Step 11 (VISUAL_ASSIST). If not, see Troubleshooting section.

## Step 11: Optional - Enable VISUAL_ASSIST

VISUAL_ASSIST provides visual feedback by displaying animated GIFs in a web browser based on the assistant's state.

### Step 11A: Prepare GIF Files

You need three animated GIF files:
1. **Thinking GIF**: Shown when bike4mind is processing the request (e.g., spinning gears, loading animation, pulsing brain)
2. **Speaking GIF**: Shown when TTS (Piper) is playing audio (e.g., animated mouth, sound waves, speech bubbles)
3. **Idle GIF**: Shown when assistant is ready/waiting (e.g., gentle breathing, blinking, subtle pulse)

**Hosting Options**:

1. **Self-hosted in Home Assistant** (recommended):
   - Upload GIFs to `/config/www/` directory
   - Access via: `http://YOUR_HA_IP:8123/local/filename.gif`
   - Example:
     ```
     /config/www/thinking.gif → http://192.168.1.100:8123/local/thinking.gif
     /config/www/speaking.gif → http://192.168.1.100:8123/local/speaking.gif
     /config/www/idle.gif → http://192.168.1.100:8123/local/idle.gif
     ```

2. **Cloud hosting**:
   - Upload to Imgur, GitHub, or similar service
   - Get public sharing URL
   - Example: `https://i.imgur.com/abc123.gif`

**GIF Recommendations**:
- Keep file size under 5MB for smooth loading
- Use simple, clear animations
- Consider accessibility (high contrast, clear visual changes)

### Step 11B: Configure VISUAL_ASSIST

1. Go to bike4mind addon **Configuration** tab
2. Enable and configure VISUAL_ASSIST:

```yaml
visual_assist_enabled: true
visual_assist_thinking_gif_url: "http://YOUR_HA_IP:8123/local/thinking.gif"
visual_assist_speaking_gif_url: "http://YOUR_HA_IP:8123/local/speaking.gif"
visual_assist_idle_gif_url: "http://YOUR_HA_IP:8123/local/idle.gif"
```

3. Click **Save**
4. Go to **Info** tab → Click **Restart**
5. Check **Log** tab for: `VISUAL_ASSIST enabled - thinking: ...`

### Step 11C: Access Visual Viewer

1. Open a web browser on any device on your local network
2. Navigate to: `http://YOUR_HA_IP:3000/visual`
   - Replace `YOUR_HA_IP` with your Home Assistant IP
   - Example: `http://192.168.1.100:3000/visual`
3. You should see:
   - Your idle GIF displayed
   - Connection status in top-right corner showing "Connected"

### Step 11D: Test VISUAL_ASSIST

1. Keep the visual viewer open in your browser
2. Ask a question to bike4mind (via voice or Assist chat)
3. Watch the GIF change through three states:
   - **Before request**: Idle GIF (ready/waiting)
   - **During bike4mind processing**: Thinking GIF (quest creation and polling, 5-30 seconds)
   - **During TTS playback**: Speaking GIF (Piper speaking, estimated duration)
   - **After TTS complete**: Returns to Idle GIF

**Use Cases**:
- Wall-mounted tablet next to voice assistant
- Desktop companion during conversations
- Visual indicator for hearing-impaired users
- Smart home dashboard integration

**Multiple Viewers**:
- Open `http://YOUR_HA_IP:3000/visual` on multiple devices simultaneously
- All viewers will stay synchronized with assistant state

For detailed VISUAL_ASSIST documentation, see [VISUAL_ASSIST.md](VISUAL_ASSIST.md)

## Step 12: Optional - Enable EXTROVERT

EXTROVERT allows Home Assistant automations to send prompts to bike4mind for AI processing, with responses spoken aloud through TTS. This creates a conversational smart home where the assistant can proactively start conversations based on events.

### Step 12A: Configure EXTROVERT

1. Go to bike4mind addon **Configuration** tab
2. Enable and configure EXTROVERT:

```yaml
extrovert_enabled: true
extrovert_rate_limit: 10
extrovert_tts_voice: "en_US-lessac-medium"  # Optional: leave blank for TTS default
```

3. **Finding Available Voices**:
   - Go to **Settings → Voice Assistants → Text-to-Speech**
   - Click on your TTS engine (e.g., Piper)
   - View the list of installed voices
   - Copy the exact voice name

4. Click **Save**
5. Go to **Info** tab → Click **Restart**
6. Check **Log** tab for: `EXTROVERT enabled - Rate limit: 10 requests per hour`

### Step 12B: Create REST Command

**Note**: This step requires editing `configuration.yaml` (cannot be done in GUI).

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

**Replace these values**:
- `YOUR_HA_IP` → Your Home Assistant IP address (from Step 5)
  - Example: `192.168.1.100`
- `YOUR_SHIM_API_KEY` → The `shim_api_key` you configured in **Step 3**
  - This is the same API key you use for Extended OpenAI Conversation
  - Example: `abc123def456...` (your 32-character hex key)
  - Find it in: bike4mind add-on → Configuration tab → `shim_api_key` field

**After editing**:
1. Save `configuration.yaml`
2. Go to **Settings → System → Restart** (or use **Developer Tools → YAML → Check Configuration** then restart)
3. Wait for Home Assistant to restart

### Step 12C: Create Test Automation

**Using Home Assistant GUI** (recommended):

1. Go to **Settings → Automations & Scenes**
2. Click **Create Automation** (bottom right)
3. Click **Create new automation** (skip blueprints)
4. Click **⋮ (menu)** in top right → **Edit in YAML**
5. Paste this automation:

```yaml
alias: "EXTROVERT - Test Trigger"
trigger:
  - platform: state
    entity_id: input_boolean.test_extrovert
    to: "on"
action:
  - action: rest_command.extrovert_trigger
    data:
      prompt: >
        This is a test at {{ now().strftime('%I:%M %p') }}. Say something
        friendly in 1 sentence to confirm you received this.
      context:
        trigger_type: test
      media_player: media_player.YOUR_SPEAKER_NAME
  - delay:
      seconds: 2
  - action: input_boolean.turn_off
    target:
      entity_id: input_boolean.test_extrovert
```

6. **Replace** `media_player.YOUR_SPEAKER_NAME` with your actual media player entity ID
   - Find available media players: **Settings → Devices & Services → Entities** → filter by "media_player"
   - Example: `media_player.living_room_speaker`
7. Click **Save** (top right)
8. Give it a name: `EXTROVERT - Test Trigger`
9. Click **Save** again

**Alternative: YAML method** (for advanced users):

Add to `configuration.yaml` and restart Home Assistant.

### Step 12D: Create Test Helper

1. Go to **Settings → Devices & Services → Helpers**
2. Click **Create Helper**
3. Select **Toggle**
4. Name: `Test EXTROVERT`
5. Entity ID: `input_boolean.test_extrovert`
6. Click **Create**

### Step 12E: Test EXTROVERT

1. Go to **Settings → Devices & Services → Helpers**
2. Find **Test EXTROVERT** toggle
3. Toggle it **ON**
4. You should hear bike4mind's response through your speaker within 5-30 seconds
5. The toggle will automatically turn off after 2 seconds

### Step 12F: Create Real Automations

**Example: Motion Detection**

```yaml
automation:
  - alias: "EXTROVERT - Living Room Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: 'on'
    condition:
      - condition: time
        after: '18:00:00'
        before: '23:00:00'
    action:
      - action: rest_command.extrovert_trigger
        data:
          prompt: >
            Someone just entered the living room at {{ now().strftime('%I:%M %p') }}.
            Say something welcoming in 1 sentence.
          context:
            trigger_type: "motion_detected"
            location: "living_room"
          media_player: "media_player.living_room_speaker"
```

**Example: Temperature Alert**

```yaml
automation:
  - alias: "EXTROVERT - High Temperature"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bedroom_temperature
        above: 78
    action:
      - action: rest_command.extrovert_trigger
        data:
          prompt: >
            The bedroom temperature is {{ states('sensor.bedroom_temperature') }}°F.
            Comment on this in a lighthearted way in 1 sentence.
          context:
            trigger_type: "temperature_alert"
          media_player: "media_player.bedroom_speaker"
```

**Prompt Engineering Tips**:
- Ask for "1 sentence" to keep responses brief
- Include tone guidance ("friendly", "lighthearted", "motivational")
- Provide context about what happened
- Use specific instructions ("greet them", "welcome them home")

For complete EXTROVERT documentation and more examples, see [EXTROVERT.md](EXTROVERT.md)

## Troubleshooting

### Add-on Won't Start

**Check logs** (Add-on → Log tab):
- Missing credentials: Ensure `b4m_api_key`, `ha_b4m_session_id`, `b4m_user_id` are set
- Port conflict: Ensure port 3000 is not in use by another service

### Extended OpenAI Conversation Won't Connect

**Check Base URL**:
- Must be `http://YOUR_LAN_IP:3000/v1` (not `localhost`)
- Test health endpoint: `curl http://YOUR_LAN_IP:3000/healthz`

**Check API Key**:
- Must match the `shim_api_key` in add-on config
- Try without auth first (remove `shim_api_key` temporarily)

### bike4mind Times Out

**Check bike4mind API**:
- Verify credentials are correct
- Test bike4mind web interface directly
- Check session ID is valid

**Increase timeout**:
- Add-on config → `timeout_ms: 90000` (90 seconds)

## Advanced Configuration

### Adjust Performance

Edit add-on configuration:

```yaml
# Faster polling (more API calls)
poll_interval_ms: 1000
poll_max_interval_ms: 3000

# Longer timeout for complex queries
timeout_ms: 90000

# Longer session before reset
session_ttl_sec: 1200
max_turns: 30
```

### Custom Tool Function Name

If your HA version uses different tool function name:

```yaml
ha_tool_function_name: "execute_action"
```

## Next Steps

- Experiment with different prompts to bike4mind
- Create custom automations triggered by bike4mind responses
- Monitor add-on logs to tune performance settings
- Try VISUAL_ASSIST feature for visual feedback (Step 11)
- Consider contributing improvements to the project

## Support

- **Specification**: See `HA_B4M_SPEC.md` in repository
- **API Documentation**: See `development_notes/B4M_API_EXAMPLE.md`
- **GitHub Issues**: [Repository URL]
