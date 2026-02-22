import asyncio
import socket
import os
from typing import Set, Dict, Any

import msgpack
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from server.frame_normalize import normalize_frame_for_ui, get_udp_port

app = FastAPI()

class TelemetryBridge:
    def __init__(self):
        self.udp_port = get_udp_port()
        self.clients: Set[WebSocket] = set()
        self.running = True

    async def broadcast(self, data: bytes):
        """Normalize and forward telemetry to all WebSocket clients."""
        if not self.clients:
            return

        # 1. Robust Decoding
        try:
            try:
                unpacked = msgpack.unpackb(data, raw=False)
            except Exception:
                unpacked = json.loads(data.decode("utf-8"))
        except Exception as e:
            print(f"Bridge Decode Error: {e}")
            return

        # 2. Normalization for UI
        ui_frame = normalize_frame_for_ui(unpacked)

        # 3. Broadcast with cleanup
        stale_clients = []
        for client in self.clients:
            try:
                await client.send_json(ui_frame)
            except Exception:
                stale_clients.append(client)
        
        for stale in stale_clients:
            self.clients.remove(stale)

    async def udp_listener(self):
        """Listen for state snapshots from the simulation."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.udp_port))
        sock.setblocking(False)

        print(f"ULTRA Bridge listening on UDP:{self.udp_port} (NEON_UDP_PORT)")

        loop = asyncio.get_event_loop()
        while self.running:
            try:
                data, addr = await loop.sock_recvfrom(sock, 65535)
                await self.broadcast(data)
            except Exception:
                await asyncio.sleep(0.001)

bridge = TelemetryBridge()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    bridge.clients.add(websocket)
    print(f"UI Client Connected. Total: {len(bridge.clients)}")
    try:
        while True:
            # Keep-alive loop
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in bridge.clients:
            bridge.clients.remove(websocket)
        print(f"UI Client Disconnected. Total: {len(bridge.clients)}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bridge.udp_listener())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
