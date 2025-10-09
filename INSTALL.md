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
2. Find **bike4mind OpenAI Shim** in the list
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
5. Verify you see: `🚀 bike4mind OpenAI Shim started`

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

## Step 9: Test Direct Conversation

Test bike4mind using the built-in Assist chat:

1. Go to **Settings → Voice Assistants → Assist**
2. In the **Conversation agent** dropdown at the top, select `bike4mind`
3. Type a message in the chat box:
   - Example: "What should I cook for dinner?"
   - Wait 5-30 seconds for bike4mind response
   - Verify you get a conversational answer

**Alternative: Create a Test Assistant**

1. Go to **Settings → Voice Assistants → Assistants**
2. Click **Add Assistant**
3. Configure:
   - **Name**: `bike4mind Test`
   - **Conversation Agent**: `bike4mind`
   - **Language**: Your preferred language
4. Click **Create**
5. Use the assistant's chat interface to test queries

If successful, proceed to Step 10. If not, see Troubleshooting section.

## Step 10: Set Up Conversation Routing (Hybrid Mode)

This enables the hybrid assist model: fast local commands + bike4mind conversations.

### 10A: Create Custom Sentences

1. Access your Home Assistant configuration directory:
   - **HA OS/Supervised**: Use File Editor add-on or SSH
   - **HA Container**: Access the config volume
   - **HA Core**: Navigate to `/home/homeassistant/.homeassistant/`

2. Create directory structure:
   ```bash
   mkdir -p custom_sentences/en
   ```

3. Create file `custom_sentences/en/bike4mind.yaml`:
   ```yaml
   language: "en"
   intents:
     ActivateBike4mind:
       data:
         - sentences:
             - "hey rosie"
             - "hi rosie"
             - "talk to rosie"
             - "let's chat"
             - "let's have a conversation"
             - "conversation mode"

     DeactivateBike4mind:
       data:
         - sentences:
             - "that's all"
             - "thanks rosie"
             - "thank you rosie"
             - "stop conversation"
             - "end conversation"
             - "return to normal mode"
             - "basic mode"

   responses:
     intents:
       ActivateBike4mind: "bike4mind activated"
       DeactivateBike4mind: "Returning to basic mode"
   ```

4. Reload conversation agent:
   - Go to **Settings → System**
   - Click **Restart** (or use **Developer Tools → YAML → Quick Reload** if available)
   - Wait for Home Assistant to restart
   - This ensures custom sentences are loaded

5. **Verify custom intents loaded**:
   - Go to **Developer Tools → Assist** tab
   - In the "Sentences parser" section:
     - Language should be: **English** (or your language)
     - Type in Sentences box: `hey rosie`
     - Click **Parse Sentences**
   - Expected result: Should show `ActivateBike4mind` intent recognized
   - If it shows "Unknown intent", the custom sentences aren't loaded yet

### 10B: Create Helper Entity

1. Go to **Settings → Devices & Services → Helpers**
2. Click **Create Helper**
3. Select **Toggle**
4. Configure:
   - **Name**: `bike4mind Conversation Mode`
   - **Icon**: `mdi:chat` (optional)
5. Click **Create**
6. Note the entity ID: `input_boolean.bike4mind_conversation_mode`

### 10C: Create Intent Scripts

Create two intent scripts to handle the custom intents:

1. Go to your Home Assistant configuration directory
2. Edit the file `configuration.yaml`
3. Add the following section:

```yaml
intent_script:
  ActivateBike4mind:
    speech:
      text: "bike4mind activated"
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.bike4mind_conversation_mode

  DeactivateBike4mind:
    speech:
      text: "Returning to basic mode"
    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.bike4mind_conversation_mode
```

4. Save the file
5. Restart Home Assistant: **Settings → System → Restart**

### 10E: Voice Assistant Routing Options

To use both fast local commands AND bike4mind conversations, you have several options:

#### Option 1: Dual Voice Assistants (Simplest)

Create two separate voice assistants with different wake words:

1. **Go to Settings → Voice Assistants → Assistants → Add Assistant**

2. **Create "Rosie" assistant**:
   - **Name**: Rosie
   - **Conversation Agent**: bike4mind (your Extended OpenAI Conversation)
   - **Language**: English
   - **Wake word**: Select an available wake word OR train a custom "rosie" wake word
     - **Note**: "rosie" is not a pre-trained wake word
     - To create custom "rosie" wake word: See https://www.home-assistant.io/voice_control/create_wake_word/
     - Training takes ~1 hour using Google Colab
     - Alternative: Use an existing wake word from your voice satellite
   - Click **Create**

3. **Keep default assistant** for fast commands:
   - Uses "hey nabu" (or your existing wake word)
   - Uses Home Assistant built-in conversation agent

**Usage**:
- "Hey Nabu, turn on the kitchen light" → Fast local command
- "Hey Rosie, what should I cook for dinner?" → bike4mind conversation

**Pros**: Simple, no custom integrations needed
**Cons**: Requires two different wake words, not all voice satellites support multiple wake words

#### Option 2: Voice Flow Integration (Dynamic Routing)

Install **Voice Flow** to route between agents using keywords:

**Installation**:

1. **Manual Installation** (HACS approval pending):
   ```bash
   cd /config
   mkdir -p custom_components
   # Download from: https://github.com/anthonymkz/Voice-Flow
   # Extract voice_flow folder to custom_components/voice_flow/
   ```

2. **Ensure voiceflow.yaml exists**:
   - Path: `config/custom_sentences/en/voiceflow.yaml`
   - This file should be included with Voice Flow

3. **Restart Home Assistant**

4. **Add Integration**:
   - Go to **Settings → Devices & Services**
   - Click **Add Integration**
   - Search for "Voice Flow"
   - Configure:
     - **Question Agent**: bike4mind (your Extended OpenAI Conversation)
     - **Command Agent**: Home Assistant (built-in)

**Usage**:
- "Hey Nabu, turn on the kitchen light" → Fast (uses default/command agent)
- "Hey Nabu, **question** what should I cook for dinner?" → bike4mind
- "Hey Nabu, **command** set living room to 50%" → Home Assistant

**How it works**:
- Voice Flow listens for keywords "question" and "command"
- "question" routes to bike4mind
- "command" routes to Home Assistant
- Queries without keywords default to Home Assistant (fast)

**Pros**: Single wake word, keyword-based routing
**Cons**: Manual installation, requires saying "question" prefix for bike4mind
**Note**: Does not use input_boolean helper; routing is keyword-based

Documentation: https://community.home-assistant.io/t/voice-flow-a-custom-integration-to-allow-multiple-conversation-agents-in-one-assistant-pipeline/796467

#### Option 3: Dynamic Pipeline Switching with Helper (CREATIVE SOLUTION!)

**This uses your input_boolean helper to automatically switch pipelines!**

**Prerequisites**:
1. You have a voice satellite device (e.g., Home Assistant Voice PE, Wyoming satellite, ESP32 voice assistant)
2. Two assist pipelines configured:
   - **"Home Assistant"** - uses built-in conversation agent (fast)
   - **"bike4mind"** - uses Extended OpenAI Conversation

**Setup**:

1. **Check if you have a voice satellite device**:
   - Go to **Developer Tools → States**
   - Search for: `assist` (not `assist_pipeline`)
   - Look for entities like: `select.DEVICE_NAME_assistant`
   - Example: `select.home_assistant_voice_09e3cd_assistant`

   **If you don't see any results**:
   - This means you don't have a physical voice satellite configured
   - This method requires hardware like:
     - Home Assistant Voice PE
     - ESP32-based voice assistant
     - Wyoming satellite device
     - Atom Echo, M5Stack, etc.
   - **Without a voice satellite, use Option 2 (Voice Flow) or Option 4 (Manual) instead**

   **If you DO see a select entity**:
   - Note the exact entity ID
   - Note what assistant options are available (e.g., "Jarvis", "B4M_Bot", "preferred")
   - Continue with step 2

2. **Create/verify two assistants exist**:
   - Go to **Settings → Voice Assistants → Assistants**
   - Ensure you have:
     - Your default assistant (e.g., "Jarvis") - uses Home Assistant conversation agent
     - Your bike4mind assistant (e.g., "B4M_Bot") - uses Extended OpenAI Conversation
   - The names must match the options available in your `select.*_assistant` entity

3. **Update intent scripts in `configuration.yaml`**:
   ```yaml
   intent_script:
     ActivateBike4mind:
       speech:
         text: "bike4mind activated"
       action:
         - service: input_boolean.turn_on
           target:
             entity_id: input_boolean.bike4mind_conversation_mode
         - service: select.select_option
           data:
             option: "B4M_Bot"  # Use your bike4mind assistant name
           target:
             entity_id: select.home_assistant_voice_09e3cd_assistant  # Replace with YOUR entity

     DeactivateBike4mind:
       speech:
         text: "Returning to basic mode"
       action:
         - service: input_boolean.turn_off
           target:
             entity_id: input_boolean.bike4mind_conversation_mode
         - service: select.select_option
           data:
             option: "Jarvis"  # Use your default assistant name
           target:
             entity_id: select.home_assistant_voice_09e3cd_assistant  # Replace with YOUR entity
   ```

   **Note**: The entity is `select.*_assistant` NOT `select.*_assist_pipeline`. These control which assistant the voice satellite uses.

4. **Restart Home Assistant**

**Usage**:
- Say: **"Hey Nabu, hey rosie"**
  - Helper turns ON
  - Pipeline switches to bike4mind
  - Response: "bike4mind activated"

- Say: **"What should I cook for dinner?"** (no wake word needed if in continuous mode)
  - Uses bike4mind (5-30 second response)

- Say: **"Hey Nabu, that's all"**
  - Helper turns OFF
  - Pipeline switches back to Home Assistant
  - Response: "Returning to basic mode"

- Say: **"Turn on the kitchen light"**
  - Uses Home Assistant (instant response)

**Pros**:
- Uses your helper toggle exactly as intended!
- Single wake word
- Automatic switching
- No additional integrations needed

**Cons**:
- Requires a voice satellite device with pipeline selector
- Must have exact pipeline names configured
- Entity ID must match your specific device

**Note**: If you have multiple voice satellites, you'll need to add all their select entities to the automation.

#### Option 4: Manual Switching (Text Chat)

For Assist text chat only (not voice):
- Manually switch conversation agent dropdown between "Home Assistant" and "bike4mind"
- Use "hey rosie" / "that's all" to toggle helper as a reminder of current mode

**Pros**: Simple, works immediately
**Cons**: Manual switching, text-only

### 10F: Set Default Conversation Agent

1. Go to **Settings → Voice Assistants → Assistants**
2. Select your primary assistant (e.g., "Home Assistant")
3. Set **Conversation Agent** to **"Home Assistant"** (the built-in one, NOT bike4mind)
4. This ensures fast local processing for basic commands

## Step 11: Test Hybrid Mode with Assist Chat

Test the setup using the Assist chat interface:

1. Go to **Settings → Voice Assistants → Assist**
2. At the top, note the **Assistant name dropdown** (e.g., "Jarvis ˅") - this lets you switch conversation agents
3. **Verify helper is OFF**:
   - Go to **Developer Tools → States**
   - Search for `input_boolean.bike4mind_conversation_mode`
   - Confirm state is `off`

### Test 1: Activate Conversation Mode
- Ensure conversation agent is set to **"Home Assistant"**
- Type in Assist chat: **"hey rosie"** (or your activation phrase)
- Expected: Response "bike4mind activated"
- Verify in **Developer Tools → States**: `input_boolean.bike4mind_conversation_mode` is now `on`

### Test 2: Manual Switch to bike4mind
- Click the **assistant name dropdown** at the top of Assist
- Select the conversation agent for bike4mind (e.g., "bike4mind" or "Extended OpenAI Conversation")
- Type: **"What should I cook for dinner?"**
- Expected:
  - 5-30 second delay
  - Conversational response from bike4mind

### Test 3: Deactivate Conversation Mode
- Switch back to **"Home Assistant"** conversation agent
- Type in Assist chat: **"that's all"** (or your deactivation phrase)
- Expected: Response "Returning to basic mode"
- Verify helper state changed to `off` in Developer Tools → States

### Test 4: Normal Mode
- With helper OFF and "Home Assistant" agent selected
- Type a basic command: **"what time is it"**
- Expected: Fast response from Home Assistant's built-in agent

**Note on Automatic Routing**:
- The routing automation (10E) is designed for voice assistants and may not work with Assist text chat
- For text chat, manually switching the conversation agent (as in Test 2) is the recommended approach
- For voice routing, see Step 12 for advanced setup

## Step 12: Test the Complete System with Voice

Once text-based routing is confirmed in Step 11, test with voice:

### Test 1: Basic Command (Fast)
- Say: **"Hey Nabu, turn on the kitchen light"**
- Expected: Instant response, light turns on
- Processed by: HA Local Assist

### Test 2: Activate Conversation Mode
- Say: **"Hey Nabu, hey Rosie"**
- Expected: Voice response "bike4mind activated"
- Helper toggle: ON

### Test 3: Conversational Query
- Say: **"What should I cook for dinner?"**
- Expected: 5-30 second delay, conversational response about cooking
- Processed by: bike4mind AI

### Test 4: Device Control via bike4mind
- Say: **"Turn on the living room light to 50% brightness"**
- Expected: Light turns on at 50% brightness
- Processed by: bike4mind with tool-calling

### Test 5: Deactivate Conversation Mode
- Say: **"That's all, thanks"**
- Expected: Voice response "Returning to basic mode"
- Helper toggle: OFF

### Test 6: Fast Command Again
- Say: **"Turn off the kitchen light"**
- Expected: Instant response
- Processed by: HA Local Assist

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

### Custom Sentences Not Working

**Error: "Unknown intent ActivateBike4mind"**

This means the custom sentences weren't loaded. Follow these steps:

1. **Verify file location and name**:
   ```
   config/
   └── custom_sentences/
       └── en/
           └── bike4mind.yaml
   ```
   - File must be exactly in this location
   - Check for typos in filename or directory names

2. **Check file permissions**:
   ```bash
   ls -la config/custom_sentences/en/bike4mind.yaml
   ```
   - File should be readable by Home Assistant

3. **Verify YAML syntax**:
   - Copy the file content to a YAML validator
   - Check indentation (use spaces, not tabs)
   - Ensure `language: "en"` matches your HA language setting

4. **Restart Home Assistant**:
   - Go to **Settings → System**
   - Click **Restart**
   - Wait for restart to complete

5. **Check Home Assistant logs**:
   - Go to **Settings → System → Logs**
   - Look for errors mentioning "intent", "conversation", or "bike4mind"
   - Common errors:
     - YAML syntax errors
     - File not found
     - Permission denied

6. **Restart Home Assistant** (if reload doesn't work):
   - Settings → System → Restart
   - Wait for full restart
   - Try Test 1 again

7. **Verify with Developer Tools**:
   - Go to **Developer Tools → Services**
   - Service: `conversation.process`
   - Service data:
     ```yaml
     text: "hey rosie"
     ```
   - Click **Call Service**
   - Check if intent is recognized

### Routing Not Working

**Check helper state**:
- Developer Tools → States → Search for `input_boolean.bike4mind_conversation_mode`
- Manually toggle to verify it changes

**Verify automation entity IDs**:
- Automations use correct conversation agent entity ID
- Replace `conversation.bike4mind` with your actual entity ID from Extended OpenAI Conversation

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

### Multiple Trigger Phrases

Add more phrases to `custom_sentences/en/bike4mind.yaml`:

```yaml
ActivateBike4mind:
  data:
    - sentences:
        - "hey rosie"
        - "activate ai"
        - "smart mode"
        - "talk to the robot"
```

### Custom Tool Function Name

If your HA version uses different tool function name:

```yaml
ha_tool_function_name: "execute_action"
```

## Optional: Enable VISUAL_ASSIST

VISUAL_ASSIST provides visual feedback by displaying animated GIFs in a web browser based on the assistant's state (speaking/idle).

### Step 13A: Prepare GIF Files

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

### Step 13B: Configure VISUAL_ASSIST

1. Go to bike4mind OpenAI Shim add-on **Configuration** tab
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

### Step 13C: Access Visual Viewer

1. Open a web browser on any device on your local network
2. Navigate to: `http://YOUR_HA_IP:3000/visual`
   - Replace `YOUR_HA_IP` with your Home Assistant IP
   - Example: `http://192.168.1.100:3000/visual`
3. You should see:
   - Your idle GIF displayed
   - Connection status in top-right corner showing "Connected"

### Step 13D: Test VISUAL_ASSIST

1. Keep the visual viewer open in your browser
2. Ask a question to bike4mind (via voice or Assist chat)
3. Watch the GIF change through three states:
   - **Before request**: Idle GIF (ready/waiting)
   - **During bike4mind processing**: Thinking GIF (quest creation and polling, 5-30 seconds)
   - **During TTS playback**: Speaking GIF (Piper speaking, 2-30 seconds estimated)
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

## Next Steps

- Experiment with different prompts to bike4mind
- Create custom automations triggered by bike4mind responses
- Monitor add-on logs to tune performance settings
- Try VISUAL_ASSIST feature for visual feedback (Step 13)
- Consider contributing improvements to the project

## Support

- **Specification**: See `HA_B4M_SPEC.md` in repository
- **API Documentation**: See `development_notes/B4M_API_EXAMPLE.md`
- **GitHub Issues**: [Repository URL]
