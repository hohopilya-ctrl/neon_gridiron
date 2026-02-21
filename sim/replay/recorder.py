import json
import os

from sim.core.state import MatchState
from sim.serialization import SimulationEncoder


class ReplayRecorder:
    """
    Professional streamable recorder for MatchState sequences.
    Writes in JSONL format for easy parsing and durability.
    """

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.file = None

    def start(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.file = open(self.output_path, "w")

    def record_frame(self, state: MatchState):
        if self.file and state:
            snapshot = SimulationEncoder.to_dict(state)
            self.file.write(json.dumps(snapshot) + "\n")
            self.file.flush()  # Ensure durability for live debugging

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None
