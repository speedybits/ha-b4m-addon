#!/usr/bin/env python3
"""
bike4mind OpenAI Shim for Home Assistant
Translates OpenAI Chat Completion API to bike4mind quest polling API
"""

import os
import time
import json
import re
import uuid
from typing import Optional, Dict, List, Any, Set
from datetime import datetime, timedelta

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel

# Configuration from environment variables
B4M_API_KEY = os.environ.get('B4M_API_KEY')
HA_B4M_SESSION_ID = os.environ.get('HA_B4M_SESSION_ID')
B4M_USER_ID = os.environ.get('B4M_USER_ID')
B4M_BASE = os.environ.get('B4M_BASE', 'https://app.bike4mind.com/api')
B4M_MODEL = os.environ.get('B4M_MODEL', 'gpt-4o-mini')
SHIM_API_KEY = os.environ.get('SHIM_API_KEY')

# Session management
SESSION_TTL_SEC = int(os.environ.get('SESSION_TTL_SEC', '600'))  # 10 minutes
MAX_TURNS = int(os.environ.get('MAX_TURNS', '20'))

# Performance tuning
TIMEOUT_MS = int(os.environ.get('TIMEOUT_MS', '60000'))  # 60 seconds
POLL_INTERVAL_MS = int(os.environ.get('POLL_INTERVAL_MS', '1500'))  # 1.5 seconds
POLL_MAX_INTERVAL_MS = int(os.environ.get('POLL_MAX_INTERVAL_MS', '5000'))  # 5 seconds

# Integration settings
HA_TOOL_FUNCTION_NAME = os.environ.get('HA_TOOL_FUNCTION_NAME', 'homeassistant.call_service')

# VISUAL_ASSIST settings
VISUAL_ASSIST_ENABLED = os.environ.get('VISUAL_ASSIST_ENABLED', 'false').lower() == 'true'
VISUAL_ASSIST_SPEAKING_GIF_URL = os.environ.get('VISUAL_ASSIST_SPEAKING_GIF_URL', '')
VISUAL_ASSIST_IDLE_GIF_URL = os.environ.get('VISUAL_ASSIST_IDLE_GIF_URL', '')

# Initialize FastAPI
app = FastAPI(title="bike4mind OpenAI Shim", version="1.2.0")

# HTTP client
http_client: Optional[httpx.AsyncClient] = None

# Session tracking (internal shim sessions)
shim_sessions: Dict[str, Dict[str, Any]] = {}

# VISUAL_ASSIST WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.current_state: str = "idle"

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        # Send current state to newly connected client
        await websocket.send_json({
            "type": "state_change",
            "state": self.current_state,
            "timestamp": int(time.time())
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_state(self, state: str):
        self.current_state = state
        message = {
            "type": "state_change",
            "state": state,
            "timestamp": int(time.time())
        }
        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        # Remove disconnected clients
        self.active_connections -= disconnected

visual_assist_manager = ConnectionManager() if VISUAL_ASSIST_ENABLED else None


# Pydantic models
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: str = "bike4mind"
    stream: bool = False
    user: Optional[str] = None


# Startup/shutdown handlers
@app.on_event("startup")
async def startup_event():
    """Initialize HTTP client on startup"""
    global http_client
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0))
    print(f"🚀 bike4mind OpenAI Shim started")
    print(f"   B4M Base: {B4M_BASE}")
    print(f"   Session ID: {HA_B4M_SESSION_ID[:8]}..." if HA_B4M_SESSION_ID else "   ⚠️ No session ID configured")
    print(f"   Auth: {'Enabled' if SHIM_API_KEY else 'Disabled (not recommended)'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close HTTP client on shutdown"""
    global http_client
    if http_client:
        await http_client.aclose()
        print("🛑 bike4mind OpenAI Shim stopped")


# Authentication dependency
async def verify_shim_auth(request: Request):
    """Verify shim API key if configured"""
    if not SHIM_API_KEY:
        return  # Auth disabled

    # Check Authorization: Bearer header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        if token == SHIM_API_KEY:
            return

    # Check X-Shim-Key header
    shim_key = request.headers.get('X-Shim-Key')
    if shim_key == SHIM_API_KEY:
        return

    raise HTTPException(status_code=401, detail="Unauthorized")


# Helper functions
def get_or_create_shim_session(user_id: Optional[str]) -> Dict[str, Any]:
    """Get or create internal shim session for tracking"""
    session_id = user_id or "default"

    if session_id not in shim_sessions:
        shim_sessions[session_id] = {
            "created": datetime.now(),
            "last_access": datetime.now(),
            "turn_count": 0
        }
    else:
        # Check TTL
        session = shim_sessions[session_id]
        age = datetime.now() - session["created"]
        if age > timedelta(seconds=SESSION_TTL_SEC) or session["turn_count"] >= MAX_TURNS:
            # Reset session
            shim_sessions[session_id] = {
                "created": datetime.now(),
                "last_access": datetime.now(),
                "turn_count": 0
            }
            print(f"♻️ Session {session_id} reset (TTL or turn limit)")
        else:
            session["last_access"] = datetime.now()

    return shim_sessions[session_id]


async def create_b4m_quest(message: str) -> Optional[str]:
    """Create bike4mind quest and return quest ID"""
    if not B4M_API_KEY or not HA_B4M_SESSION_ID or not B4M_USER_ID:
        raise HTTPException(status_code=500, detail="bike4mind credentials not configured")

    payload = {
        "sessionId": HA_B4M_SESSION_ID,
        "message": message,
        "historyCount": 10,
        "fabFileIds": [],
        "messageFileIds": [],
        "params": {
            "model": B4M_MODEL,
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False
        },
        "promptMeta": {
            "session": {
                "id": HA_B4M_SESSION_ID,
                "userId": B4M_USER_ID
            }
        }
    }

    headers = {
        "X-API-Key": B4M_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = await http_client.post(
            f"{B4M_BASE}/ai/llm",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        # Quest ID may be in 'id' or 'questId' field
        quest_id = data.get('questId') or data.get('id')
        if not quest_id:
            print(f"⚠️ No quest ID in response: {data}")
            return None

        return quest_id
    except httpx.HTTPError as e:
        print(f"❌ bike4mind quest creation failed: {e}")
        raise HTTPException(status_code=502, detail=f"bike4mind API error: {str(e)}")


async def poll_b4m_quest(quest_id: str) -> Optional[str]:
    """Poll bike4mind quest until done, return response text"""
    headers = {
        "X-API-Key": B4M_API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.time()
    timeout_sec = TIMEOUT_MS / 1000
    poll_interval = POLL_INTERVAL_MS / 1000
    attempt = 0

    while True:
        attempt += 1
        elapsed = time.time() - start_time

        if elapsed > timeout_sec:
            raise HTTPException(status_code=504, detail="bike4mind quest timeout")

        try:
            response = await http_client.get(
                f"{B4M_BASE}/sessions/{HA_B4M_SESSION_ID}/chat/{quest_id}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            status = data.get('status')

            if status == 'done':
                # Extract response (priority order)
                ai_reply = None

                # 1. Check replies array
                if data.get('replies') and isinstance(data['replies'], list):
                    ai_reply = '\n'.join(data['replies'])
                # 2. Check reply field
                elif data.get('reply'):
                    ai_reply = data['reply']
                # 3. Check questMasterReply
                elif data.get('questMasterReply'):
                    ai_reply = data['questMasterReply']
                # 4. Check researchModeResults
                elif data.get('researchModeResults'):
                    results = [r.get('response') for r in data['researchModeResults'] if r.get('response')]
                    if results:
                        ai_reply = '\n\n'.join(results)

                if not ai_reply:
                    raise HTTPException(status_code=500, detail="bike4mind quest done but no reply found")

                return ai_reply

            elif status == 'stopped':
                raise HTTPException(status_code=500, detail="bike4mind quest stopped")

            elif status == 'running':
                # Continue polling with backoff
                await asyncio.sleep(poll_interval)
                # Exponential backoff up to max
                poll_interval = min(poll_interval * 1.2, POLL_MAX_INTERVAL_MS / 1000)

            else:
                print(f"⚠️ Unknown quest status: {status}")
                await asyncio.sleep(poll_interval)

        except httpx.HTTPError as e:
            print(f"⚠️ Polling error (attempt {attempt}): {e}")
            await asyncio.sleep(poll_interval)


def extract_tool_calls(response_text: str) -> Optional[List[Dict[str, Any]]]:
    """Extract JSON tool-call from bike4mind response"""
    # Look for JSON code blocks
    pattern = r'```json\s*(\{.*?\})\s*```'
    matches = re.findall(pattern, response_text, re.DOTALL)

    if not matches:
        return None

    tool_calls = []
    for match in matches:
        try:
            data = json.loads(match)

            # Check if it's a Home Assistant action
            if data.get('action') == 'call_service':
                tool_call = {
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": HA_TOOL_FUNCTION_NAME,
                        "arguments": json.dumps({
                            "domain": data.get('domain'),
                            "service": data.get('service'),
                            "entity_id": data.get('entity_id'),
                            "data": data.get('data', {})
                        })
                    }
                }
                tool_calls.append(tool_call)
        except json.JSONDecodeError:
            continue

    return tool_calls if tool_calls else None


# API endpoints
@app.get("/healthz")
async def health_check():
    """Health check endpoint (no auth required)"""
    return {"status": "healthy", "service": "bike4mind-shim"}


@app.post("/v1/chat/completions", dependencies=[Depends(verify_shim_auth)])
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""

    # Get or create shim session
    shim_session = get_or_create_shim_session(request.user)
    shim_session["turn_count"] += 1

    # Extract last message
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = request.messages[-1].content

    # Broadcast "speaking" state if VISUAL_ASSIST enabled
    if VISUAL_ASSIST_ENABLED and visual_assist_manager:
        await visual_assist_manager.broadcast_state("speaking")

    try:
        # Create bike4mind quest
        print(f"🤖 Creating bike4mind quest: {last_message[:50]}...")
        quest_id = await create_b4m_quest(last_message)

        if not quest_id:
            raise HTTPException(status_code=502, detail="Failed to create bike4mind quest")

        # Poll for response
        print(f"⏳ Polling quest {quest_id}...")
        response_text = await poll_b4m_quest(quest_id)

        print(f"✅ bike4mind response received ({len(response_text)} chars)")

        # Extract tool calls
        tool_calls = extract_tool_calls(response_text)

        # Build OpenAI response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

        if request.stream:
            # Streaming response
            async def generate_stream():
                # Send content chunks
                if response_text:
                    yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'bike4mind', 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': response_text}, 'finish_reason': None}]})}\n\n"

                # Send tool_calls in final chunk if present
                if tool_calls:
                    yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'bike4mind', 'choices': [{'index': 0, 'delta': {'tool_calls': tool_calls}, 'finish_reason': 'tool_calls'}]})}\n\n"
                else:
                    yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'bike4mind', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"

                yield "data: [DONE]\n\n"

            # Return to idle after streaming completes
            if VISUAL_ASSIST_ENABLED and visual_assist_manager:
                await visual_assist_manager.broadcast_state("idle")

            return StreamingResponse(generate_stream(), media_type="text/event-stream")

        else:
            # Non-streaming response
            response = {
                "id": completion_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "bike4mind",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "tool_calls" if tool_calls else "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

            # Add tool_calls if present
            if tool_calls:
                response["choices"][0]["message"]["tool_calls"] = tool_calls

            # Return to idle after response is ready
            if VISUAL_ASSIST_ENABLED and visual_assist_manager:
                await visual_assist_manager.broadcast_state("idle")

            return JSONResponse(response)

    except Exception as e:
        # Return to idle on any error
        if VISUAL_ASSIST_ENABLED and visual_assist_manager:
            await visual_assist_manager.broadcast_state("idle")
        raise


@app.post("/admin/reset_session", dependencies=[Depends(verify_shim_auth)])
async def reset_session(request: Request):
    """Reset internal shim session"""
    data = await request.json()
    user_id = data.get('user_id', 'default')

    if user_id in shim_sessions:
        del shim_sessions[user_id]
        return {"status": "reset", "user_id": user_id}

    return {"status": "not_found", "user_id": user_id}


# Missing import
import asyncio


# VISUAL_ASSIST endpoints (conditionally registered)
if VISUAL_ASSIST_ENABLED:
    @app.get("/visual", response_class=HTMLResponse)
    async def visual_page():
        """Serve HTML viewer page with embedded GIF URLs"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Voice Assistant Visual</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }}
        #assistant-gif {{
            max-width: 100%;
            max-height: 100vh;
            object-fit: contain;
        }}
        .status {{
            position: fixed;
            top: 10px;
            right: 10px;
            color: white;
            font-family: monospace;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <img id="assistant-gif" src="{VISUAL_ASSIST_IDLE_GIF_URL}" alt="Assistant">
    <div class="status">
        <span id="connection-status">Connecting...</span>
    </div>
    <script>
        // Embed GIF URLs from server configuration
        const SPEAKING_GIF_URL = "{VISUAL_ASSIST_SPEAKING_GIF_URL}";
        const IDLE_GIF_URL = "{VISUAL_ASSIST_IDLE_GIF_URL}";

        // WebSocket client
        class VisualAssistClient {{
            constructor() {{
                this.ws = null;
                this.reconnectInterval = 2000;
                this.gifElement = document.getElementById('assistant-gif');
                this.statusElement = document.getElementById('connection-status');
                this.connect();
            }}

            connect() {{
                const wsUrl = `ws://${{window.location.host}}/ws`;
                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {{
                    console.log('Connected to Visual Assist');
                    this.statusElement.textContent = 'Connected';
                    this.statusElement.style.color = 'lime';
                }};

                this.ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    if (data.type === 'state_change') {{
                        this.updateGif(data.state);
                    }}
                }};

                this.ws.onerror = (error) => {{
                    console.error('WebSocket error:', error);
                    this.statusElement.textContent = 'Error';
                    this.statusElement.style.color = 'red';
                }};

                this.ws.onclose = () => {{
                    console.log('Disconnected, reconnecting...');
                    this.statusElement.textContent = 'Reconnecting...';
                    this.statusElement.style.color = 'yellow';
                    setTimeout(() => this.connect(), this.reconnectInterval);
                }};
            }}

            updateGif(state) {{
                const gifSrc = state === 'speaking' ? SPEAKING_GIF_URL : IDLE_GIF_URL;
                if (this.gifElement.src !== gifSrc) {{
                    this.gifElement.src = gifSrc + '?t=' + Date.now(); // Cache bust
                }}
            }}
        }}

        // Initialize client
        const client = new VisualAssistClient();
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time state updates"""
        await visual_assist_manager.connect(websocket)
        try:
            while True:
                # Keep connection alive and handle pings
                data = await websocket.receive_json()
                if data.get("type") == "ping":
                    await websocket.send_json({{
                        "type": "pong",
                        "state": visual_assist_manager.current_state
                    }})
        except WebSocketDisconnect:
            visual_assist_manager.disconnect(websocket)

    @app.get("/visual/status")
    async def visual_status():
        """Return current assistant state and configuration"""
        return {{
            "state": visual_assist_manager.current_state,
            "visual_assist_enabled": True,
            "speaking_gif_url": VISUAL_ASSIST_SPEAKING_GIF_URL,
            "idle_gif_url": VISUAL_ASSIST_IDLE_GIF_URL
        }}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
