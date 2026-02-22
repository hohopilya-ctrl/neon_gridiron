import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .ws_hub import hub
from .udp_ingest import ingest

app = FastAPI(title="Neon Gridiron ULTRA: Telemetry Hub v2")

@app.get("/")
async def root():
    return {"status": "online", "version": "2.2.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """Canonical WebSocket endpoint for the UI live broadcast."""
    await hub.register(websocket)
    try:
        while True:
            # Keep alive and receive any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.unregister(websocket)

@app.websocket("/ws/state")
async def websocket_legacy(websocket: WebSocket):
    """Legacy endpoint, redirecting to /ws/live logic."""
    await websocket_live(websocket)

@app.on_event("startup")
async def startup_event():
    # Start background tasks
    asyncio.create_task(hub.broadcast_loop())
    asyncio.create_task(ingest.start())
