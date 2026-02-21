import json
import socket

from sim.serialization import SimulationEncoder


class UDPSender:
    def __init__(self, ip="127.0.0.1"):
        self.ip = ip
        self.target_ports = [4242, 4243]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_state(self, state, extra_data: dict = None):
        """Broadcasts encoded simulation state via UDP."""
        try:
            state_dict = SimulationEncoder.to_dict(state)
            if extra_data:
                state_dict.update(extra_data)

            payload = json.dumps(state_dict).encode("utf-8")

            for port in self.target_ports:
                try:
                    self.sock.sendto(payload, (self.ip, port))
                except Exception:
                    pass
        except Exception as e:
            print(f"Telemetry Error: {e}")


# lines: 60
