from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Neon Gridiron ULTRA: Telemetry Hub")


class ConnectionManager:
    """Manages WebSocket connections for real-time state broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Handle stale connections
                pass


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"status": "online", "service": "neon-gridiron-telemetry"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/state")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Maintain connection, maybe receive client pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
