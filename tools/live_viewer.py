import json
import socket
from typing import Any, Dict

import pygame


class LiveViewer:
    """
    High-performance 2D visualizer for Neon Gridiron telemetry.
    Receives UDP packets and renders the futuristic arena state.
    """

    def __init__(self, port: int = 4242):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Neon Gridiron ULTRA: Live Telemetry")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        self.sock.setblocking(False)

        self.clock = pygame.time.Clock()
        self.colors = {
            "bg": (10, 10, 20),
            "pitch": (20, 30, 50),
            "blue": (0, 200, 255),
            "red": (255, 0, 100),
            "ball": (0, 255, 100),
            "walls": (100, 255, 255),
        }

    def run(self):
        running = True
        state = None

        print(f"📺 Viewer active on port {self.sock.getsockname()[1]}")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Drain UDP buffer
            while True:
                try:
                    data, _ = self.sock.recvfrom(65535)
                    state = json.loads(data.decode("utf-8"))
                except BlockingIOError:
                    break
                except Exception as e:
                    print(f"Viewer Error: {e}")
                    break

            self._draw(state)
            self.clock.tick(60)

        pygame.quit()

    def _draw(self, state: Optional[Dict[str, Any]]):
        self.screen.fill(self.colors["bg"])

        # Draw Pitch
        pygame.draw.rect(self.screen, self.colors["pitch"], (50, 100, 700, 400), borderRadius=20)
        pygame.draw.rect(self.screen, self.colors["walls"], (50, 100, 700, 400), 2, borderRadius=20)

        if state:
            # Draw Ball
            bx, by = state["b"]["p"]
            # Scale 600x400 to 700x400 centered
            px = 50 + (bx / 600.0) * 700
            py = 100 + (by / 400.0) * 400
            pygame.draw.circle(self.screen, self.colors["ball"], (int(px), int(py)), 8)

            # Draw Players
            for p in state["p"]:
                px = 50 + (p["pos"][0] / 600.0) * 700
                py = 100 + (p["pos"][1] / 400.0) * 400
                color = self.colors["blue"] if p["team"] == 0 else self.colors["red"]
                pygame.draw.circle(self.screen, color, (int(px), int(py)), 12)

            # Draw Score
            # ... (UI text logic)

        pygame.display.flip()


if __name__ == "__main__":
    viewer = LiveViewer()
    viewer.run()
