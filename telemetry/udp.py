import json
import socket

from sim.core.state import MatchState
from sim.serialization import SimulationEncoder


class UDPSender:
    """
    Broadcasts simulation state over UDP for low-latency visualizers.
    Decoupled from the Environment for universal usage.
    """

    def __init__(self, ip: str = "127.0.0.1", ports: list = None):
        self.ip = ip
        self.target_ports = ports or [4242, 4243]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_state(self, state: MatchState, extra_data: dict = None):
        """Encodes and broadcasts a MatchState snapshot."""
        try:
            data = SimulationEncoder.to_dict(state)
            if extra_data:
                data.update(extra_data)

            payload = json.dumps(data).encode("utf-8")

            for port in self.target_ports:
                try:
                    self.sock.sendto(payload, (self.ip, port))
                except Exception:
                    pass
        except Exception:
            # Silent fail for telemetry to avoid crashing simulation
            pass

    def close(self):
        self.sock.close()
