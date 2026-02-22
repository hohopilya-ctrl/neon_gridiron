import asyncio
import socket
from typing import Set

import msgpack
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class TelemetryBridge:
    def __init__(self, udp_port: int = 5555):
        self.udp_port = udp_port
        self.clients: Set[WebSocket] = set()
        self.running = True

    async def broadcast(self, data: bytes):
        """Forward msgpack data to all connected WebSocket clients."""
        if not self.clients:
            return
            
        # Unpack to verify/log or just forward raw
        # For ULTRA efficiency, we could forward raw, but UI expects JSON for now
        # Let's convert to JSON-compatible for the current browser UI
        try:
            unpacked = msgpack.unpackb(data, raw=False)
            message = unpacked # Already a dict
            
            # Use gather to broadcast in parallel
            tasks = [client.send_json(message) for client in self.clients]
            if tasks:
                await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Bridge Broadcast Error: {e}")

    async def udp_listener(self):
        """Listen for state snapshots from the simulation."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.udp_port))
        sock.setblocking(False)
        
        print(f"ULTRA Bridge listening on UDP:{self.udp_port}")
        
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
            await websocket.receive_text() # Keep-alive
    except WebSocketDisconnect:
        bridge.clients.remove(websocket)
        print(f"UI Client Disconnected. Total: {len(bridge.clients)}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bridge.udp_listener())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
