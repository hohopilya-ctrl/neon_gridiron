from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging

# Configure Professional Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NeonServer")

app = FastAPI(title="Neon Evolution League API", version="2.0.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Automatic cleanup of stale connections
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/health")
def health():
    return {"status": "operational", "version": "2.0.0", "engine": "ultra"}

@app.get("/api/v1/league/stats")
async def get_league_stats():
    # In a real app, this would query a database/pool manager
    return {
        "active_models": 1,
        "generations_completed": 5,
        "system_status": "training"
    }

@app.websocket("/ws/live")
async def live_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Maintain connection, wait for client pings if needed
            data = await websocket.receive_text()
            # Handle client-to-server commands if any
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket)

async def broadcast_state(state: dict):
    payload = json.dumps(state)
    await manager.broadcast(payload)
# lines: 40
