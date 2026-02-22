import asyncio
import json
from typing import Set
from fastapi import WebSocket

class WebSocketHub:
    """Manages WebSocket clients and handles real-time broadcasting."""
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=4)

    async def register(self, ws: WebSocket):
        await ws.accept()
        self.clients.add(ws)
        print(f"WS Hub: Client connected. Total: {len(self.clients)}")

    def unregister(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)
            print(f"WS Hub: Client disconnected. Total: {len(self.clients)}")

    async def broadcast_loop(self):
        """Background task to broadcast frames from the queue to all clients."""
        while True:
            frame = await self.queue.get()
            if not self.clients:
                continue
                
            payload = json.dumps(frame)
            
            # Send to all clients, cleaning up broken ones
            stale = []
            for client in self.clients:
                try:
                    await client.send_text(payload)
                except Exception:
                    stale.append(client)
            
            for s in stale:
                self.unregister(s)
            
            self.queue.task_done()

    def push_frame(self, frame: dict):
        """Pushes a frame to the broadcast queue. Drops old if full."""
        if self.queue.full():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except asyncio.QueueEmpty:
                pass
        self.queue.put_nowait(frame)

hub = WebSocketHub()
