import asyncio
import socket

import msgpack

from .frame_protocol import normalize_frame
from .ws_hub import hub


class UDPIngest:
    """Ingests legacy UDP telemetry and pushes it to the WS hub."""

    def __init__(self, port: int = 4242):
        self.port = port
        self.running = True

    async def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.port))
        sock.setblocking(False)

        print(f"UDP Ingest: Listening on port {self.port}")

        loop = asyncio.get_event_loop()
        while self.running:
            try:
                data, addr = await loop.sock_recvfrom(sock, 65535)
                # 1. Unpack legacy (msgpack)
                legacy_frame = msgpack.unpackb(data, raw=False)

                # 2. Normalize to v2.2.0
                canonical = normalize_frame(legacy_frame)

                # 3. Push to hub
                hub.push_frame(canonical)
            except Exception:
                # Tight loop, minimal sleep on error
                await asyncio.sleep(0.001)


ingest = UDPIngest()
