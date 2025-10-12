# EXTROVERT Feature Specification

## Overview

EXTROVERT allows Home Assistant automations to send prompts to bike4mind for AI processing, with the response spoken aloud through TTS. The automation defines the prompt text, which is sent to bike4mind just like a user conversation. This creates a conversational smart home where the assistant can proactively start conversations based on events.

## Purpose

EXTROVERT is designed to make your smart home feel more conversational and alive. Rather than silently reacting to events, your home can initiate natural conversations when interesting things happen.

## Use Cases

Automations send prompts to bike4mind asking it to start conversations:

1. **Motion Detection**:
   - Automation prompt: "Someone just entered the living room at 3:35 PM. Come up with 1 sentence to greet them."
   - bike4mind response: "Hey there! Perfect timing - I was just thinking about you."

2. **Temperature Changes**:
   - Automation prompt: "The bedroom temperature just reached 78°F, which is warmer than usual. Say something about this in 1 sentence."
   - bike4mind response: "It's getting toasty in here! Feeling warm?"

3. **Security Events**:
   - Automation prompt: "The front door just opened at 5:30 PM. Welcome whoever just arrived home with 1 sentence."
   - bike4mind response: "Welcome home! How was your day?"

4. **Device Status**:
   - Automation prompt: "The washing machine cycle just finished. Let me know in 1 sentence."
   - bike4mind response: "Heads up - the laundry's done!"

5. **Time-Based Events**:
   - Automation prompt: "It's 8:00 AM on a Monday morning. Say something motivational in 1 sentence."
   - bike4mind response: "Good morning! Let's make this Monday amazing!"

## Architecture

### High-Level Flow

```
Home Assistant Automation triggers
        ↓
    Automation crafts a prompt asking bike4mind to say something
        ↓
    HTTP POST to /v1/extrovert/trigger
        ↓
    bike4mind receives prompt (like a user message)
        ↓
    bike4mind generates conversational response
        ↓
    Response spoken via Home Assistant TTS
```

**Key Point**: The automation writes the prompt that tells bike4mind what kind of thing to say. The prompt is sent to bike4mind exactly like a user conversation message.

### Key Components

1. **API Endpoint**: `/v1/extrovert/trigger` - Accepts prompts from automations
2. **bike4mind Integration**: Processes prompt and generates conversational response
3. **TTS Integration**: Speaks response through Home Assistant TTS
4. **Rate Limiting**: Prevents automation spam (configurable, default: 10/hour)
5. **Busy State**: Rejects concurrent requests to prevent interruptions

## API Endpoint

### POST /v1/extrovert/trigger

**Request fields:**
- `prompt` - The text prompt sent to bike4mind (required)
- `context` - Optional metadata about the trigger (for logging/debugging)
- `tts_config` - TTS configuration (media player, optional voice override)

**Response fields:**
- `status` - success, ignored, rate_limited, or error
- `quest_id` - bike4mind quest identifier
- `response` - The generated text that was spoken
- `tts_triggered` - Whether TTS was successfully triggered

## Configuration

### Add-on Configuration

Three configuration options in the bike4mind shim add-on:

- **extrovert_enabled**: Enable/disable feature (default: disabled)
- **extrovert_rate_limit**: Max requests per hour (default: 10, range: 1-100)
- **extrovert_tts_voice**: Voice name for responses (optional, blank = TTS default)

### Finding Available Voices

To see available voices in Home Assistant:
1. Go to **Settings → Voice Assistants → Text-to-Speech**
2. Click on your TTS engine (e.g., Piper)
3. View the list of installed voices
4. Copy the exact voice name (e.g., `en_US-lessac-medium`)
5. Paste into **extrovert_tts_voice** configuration field

## Home Assistant Integration

### Setup Steps

1. **Enable EXTROVERT** in the bike4mind shim add-on configuration
2. **Configure a REST command** in Home Assistant's `configuration.yaml` to call the EXTROVERT endpoint
3. **Create automations** that call the REST command with appropriate prompts

### REST Command

Create a REST command in Home Assistant that:
- Posts to `http://YOUR_HA_IP:3000/v1/extrovert/trigger`
- Includes authorization header with your shim API key
- Accepts `prompt`, `context`, and `media_player` parameters

### Automation Structure

Automations should:
1. Trigger on an event (motion, temperature, door open, time, etc.)
2. Include conditions to prevent excessive triggering
3. Call the REST command with a prompt asking bike4mind to say something
4. Specify which media player to use for TTS

## Prompt Engineering Guidelines

The automation writes the prompt that tells bike4mind what kind of thing to say. These prompts should instruct bike4mind to generate brief, conversational responses.

### How It Works

1. Automation triggers on an event
2. Automation builds a prompt asking bike4mind to say something about the event
3. Prompt is sent to bike4mind (just like a user message)
4. bike4mind generates a conversational response
5. Response is spoken via TTS

### Prompt Best Practices

**Do:**
- Ask bike4mind to generate 1 sentence (keeps responses brief)
- Provide context about what happened
- Be conversational and natural
- Use specific instructions ("greet them", "say something funny", "welcome them home")
- Include tone guidance in your prompts ("friendly", "lighthearted", "motivational")

**Don't:**
- Make prompts too long (under 50 words is ideal)
- Include technical details or entity IDs
- Use markdown formatting
- Try to control devices (EXTROVERT is for conversation only)

### Good Prompt Examples

```
Someone just entered the kitchen at 2:15 PM. Say something welcoming in 1 sentence.

The bedroom temperature reached 75°F. Comment on this in a lighthearted way in 1 sentence.

It's 8:00 AM on a workday. Say something motivational and energetic in 1 sentence.

The front door opened at 6:00 PM. Welcome whoever arrived home in a friendly tone in 1 sentence.

Motion detected in the garage at 11:00 PM. Ask if everything is okay in a casual way in 1 sentence.
```

### Bad Prompt Examples

```
❌ binary_sensor.kitchen_motion changed to 'on' at 14:15:32
   (Too technical)

❌ Should I turn on the lights in the living room?
   (Asking about device control, not conversation)

❌ This is a very detailed explanation of everything that happened...
   (Too long - keep it brief)
```

### Using Home Assistant Templating

Automations can use Home Assistant templating to build dynamic prompts with real-time sensor data, time information, and state values.

## Response Handling

### How bike4mind Processes Prompts

When EXTROVERT sends a prompt to bike4mind:

1. Prompt is sent as a user message to bike4mind quest API
2. bike4mind processes it with the same AI model as interactive conversations
3. bike4mind generates a natural language response based on the prompt
4. Response is sanitized and spoken via TTS

**The prompt from the automation IS the input to bike4mind** - it's sent directly, not pre-processed or transformed.

### Response Sanitization

bike4mind responses are automatically sanitized before TTS:
- Strips markdown formatting
- Removes JSON blocks (prevents device control attempts)
- Truncates to 200 words max
- Cleans up technical formatting

Good prompt engineering (asking for 1 sentence) should result in brief responses that need minimal sanitization.

### Error Handling

Errors are logged but **not spoken** to prevent disruptive notifications:
- Timeout: Silent failure, logged
- bike4mind error: Silent failure, logged
- TTS unavailable: Silent failure, logged
- Media player offline: Silent failure, logged

This prevents 3 AM error announcements from automation issues.

## Rate Limiting & Concurrency

### Rate Limiting

- **Default**: 10 requests per hour
- **Rolling window**: Not reset at top of hour
- **Exceeded limit**: Returns HTTP 429, not spoken
- **Purpose**: Prevents automation spam and API quota exhaustion

Configure higher limits for busy households, lower for quieter environments.

### Busy State Management

- **One request at a time**: New requests rejected if assistant is busy
- **No queue**: Rejected requests return `status: "ignored"`
- **Rationale**: Prevents interruptions and overlapping speech

Configure automations with proper conditions to prevent excessive triggering.

## VISUAL_ASSIST Integration

EXTROVERT integrates with the existing VISUAL_ASSIST feature:
- **Thinking state**: Displayed while bike4mind processes prompt
- **Speaking state**: Displayed during TTS playback
- **Idle state**: Displayed when complete

## Design Decisions

### 1. Conversation Focused
**Decision**: EXTROVERT is for starting conversations, not controlling devices
**Rationale**: Creates natural interactions; automation conditions already handle when to speak

### 2. Automation Defines Prompts
**Decision**: Automation writes the prompt that bike4mind processes
**Rationale**: Maximum flexibility; user controls exactly what the AI is asked to say

### 3. No Concurrent Request Queue
**Decision**: Reject new requests while busy, don't queue them
**Rationale**: Simpler implementation, prevents stale responses

### 4. Silent Error Handling
**Decision**: Log errors but never speak them
**Rationale**: Prevents disruptive error announcements, especially at night

### 5. Manual Voice Configuration
**Decision**: User specifies voice in config, not auto-discovered
**Rationale**: Simpler, more reliable, works with any TTS service

### 6. No Tool Calling
**Decision**: Strip all JSON blocks from responses
**Rationale**: EXTROVERT is for conversation only, not device control

### 7. Prompt Engineering First
**Decision**: Rely on good prompts (asking for 1 sentence) rather than aggressive filtering
**Rationale**: Better results from clear instructions than post-processing

### 8. HA Automations Handle Timing
**Decision**: Don't implement do-not-disturb mode in EXTROVERT
**Rationale**: HA automation conditions are powerful enough to handle scheduling

## Testing

### Manual Test

Create an input boolean in Home Assistant and an automation that triggers EXTROVERT when the boolean is turned on. Use a simple test prompt like "This is a test. Say something in 1 sentence to confirm you received this."

Toggle the input boolean to trigger a test conversation.

## Implementation Notes

- Uses existing bike4mind quest API
- Uses the same `ha_b4m_session_id` as interactive conversations (maintains context continuity)
- Polls for response with exponential backoff
- Calls Home Assistant `tts.speak` service
- Requires supervisor token for HA API access
- Uses same authentication as main OpenAI shim endpoint

### Session Context

EXTROVERT uses the **same session ID** as interactive conversations with bike4mind. This means:
- bike4mind remembers what it said via EXTROVERT
- Users can reference EXTROVERT comments in their conversations
- bike4mind can reference previous EXTROVERT context (e.g., "As I mentioned earlier...")
- Unified conversation history across both EXTROVERT and interactive use

## Security

- Same authentication as OpenAI shim (API key)
- Never exposed to internet (LAN only)
- No device control capability
- Rate limiting prevents abuse
- Silent failures prevent information disclosure

## Limitations

### 1. No Automatic Listening After TTS (Important)

**Home Assistant does not currently support automatic listening after TTS responses without requiring a wake word.**

After EXTROVERT speaks a response via TTS, the voice assistant will NOT automatically start listening for a follow-up. Users must say the wake word again to respond.

**Why This Matters:**
- Questions like "How was your day?" won't get immediate voice responses
- Users need to manually trigger the assistant (wake word or button) to reply
- This is a Home Assistant platform limitation, not an EXTROVERT limitation

**Best Practices Given This Limitation:**

✅ **Design for one-way announcements:**
- "The laundry is done!"
- "Welcome home!"
- "The bedroom is getting warm."

✅ **Use rhetorical or optional questions:**
- "How was your day?" (understanding no immediate response expected)
- "Need anything?" (users can choose to respond later via wake word)

❌ **Avoid expecting immediate two-way conversation:**
- Don't design prompts that require immediate follow-up responses
- Don't expect natural back-and-forth conversation flow

**Technical Background:**

Home Assistant's voice pipeline architecture doesn't support "continued conversation" mode where the assistant automatically listens after speaking. This feature has been requested in the HA community (GitHub architecture discussion #1022) but is not yet implemented due to challenges with:
- Maintaining conversation context
- Intent matching for follow-up responses
- Determining when to stop listening

**Future Possibility:**

If Home Assistant adds continued conversation support in the future, EXTROVERT could be enhanced to support automatic listening after TTS responses.

### 2. Other Limitations

- One request at a time (no queue)
- 5-30 second response latency
- Rate limited to prevent spam
- No cost tracking
- No per-location voice configuration
- Requires internet for bike4mind API
- No urgent/priority mode
