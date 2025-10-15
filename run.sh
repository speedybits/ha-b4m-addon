#!/usr/bin/with-contenv bashio

# Read configuration from Home Assistant add-on options
export B4M_API_KEY=$(bashio::config 'b4m_api_key')
export HA_B4M_SESSION_ID=$(bashio::config 'ha_b4m_session_id')
export B4M_USER_ID=$(bashio::config 'b4m_user_id')
export SHIM_API_KEY=$(bashio::config 'shim_api_key')
export B4M_MODEL=$(bashio::config 'b4m_model')
export SESSION_TTL_SEC=$(bashio::config 'session_ttl_sec')
export MAX_TURNS=$(bashio::config 'max_turns')
export TIMEOUT_MS=$(bashio::config 'timeout_ms')
export POLL_INTERVAL_MS=$(bashio::config 'poll_interval_ms')
export POLL_MAX_INTERVAL_MS=$(bashio::config 'poll_max_interval_ms')
export B4M_BASE=$(bashio::config 'b4m_base')
export HA_TOOL_FUNCTION_NAME=$(bashio::config 'ha_tool_function_name')

# Export VISUAL_ASSIST configuration
if bashio::config.true 'visual_assist_enabled'; then
    export VISUAL_ASSIST_ENABLED=true
    export VISUAL_ASSIST_THINKING_GIF_URL=$(bashio::config 'visual_assist_thinking_gif_url')
    export VISUAL_ASSIST_SPEAKING_GIF_URL=$(bashio::config 'visual_assist_speaking_gif_url')
    export VISUAL_ASSIST_IDLE_GIF_URL=$(bashio::config 'visual_assist_idle_gif_url')

    # Validate URLs are non-empty
    if [ -z "$VISUAL_ASSIST_THINKING_GIF_URL" ] || [ -z "$VISUAL_ASSIST_SPEAKING_GIF_URL" ] || [ -z "$VISUAL_ASSIST_IDLE_GIF_URL" ]; then
        bashio::log.fatal "visual_assist_enabled is true but GIF URLs are not configured"
        exit 1
    fi

    bashio::log.info "VISUAL_ASSIST enabled - thinking: ${VISUAL_ASSIST_THINKING_GIF_URL}"
    bashio::log.info "VISUAL_ASSIST enabled - speaking: ${VISUAL_ASSIST_SPEAKING_GIF_URL}"
    bashio::log.info "VISUAL_ASSIST enabled - idle: ${VISUAL_ASSIST_IDLE_GIF_URL}"
else
    export VISUAL_ASSIST_ENABLED=false
fi

# Export EXTROVERT configuration
if bashio::config.true 'extrovert_enabled'; then
    export EXTROVERT_ENABLED=true
    export EXTROVERT_HA_URL="http://supervisor/core/api"
    export EXTROVERT_HA_TOKEN="${SUPERVISOR_TOKEN}"
    export EXTROVERT_RATE_LIMIT=$(bashio::config 'extrovert_rate_limit')
    export EXTROVERT_TTS_ENTITY_ID=$(bashio::config 'extrovert_tts_entity_id')
    export EXTROVERT_TTS_VOICE=$(bashio::config 'extrovert_tts_voice')

    bashio::log.info "EXTROVERT enabled - Rate limit: ${EXTROVERT_RATE_LIMIT} requests per hour"
    bashio::log.info "EXTROVERT TTS entity: ${EXTROVERT_TTS_ENTITY_ID}"
    if [ -n "${EXTROVERT_TTS_VOICE}" ]; then
        bashio::log.info "EXTROVERT TTS voice: ${EXTROVERT_TTS_VOICE}"
    else
        bashio::log.info "EXTROVERT TTS voice: using service default"
    fi
else
    export EXTROVERT_ENABLED=false
fi

# Validate required configuration
if [ -z "$B4M_API_KEY" ]; then
    bashio::log.fatal "b4m_api_key is required"
    exit 1
fi

if [ -z "$HA_B4M_SESSION_ID" ]; then
    bashio::log.fatal "ha_b4m_session_id is required"
    exit 1
fi

if [ -z "$B4M_USER_ID" ]; then
    bashio::log.fatal "b4m_user_id is required"
    exit 1
fi

bashio::log.info "Starting bike4mind addon..."

# Run the Python application
exec python3 /app/app.py
