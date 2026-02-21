import json
import os
from typing import List
from sim.core.state import MatchState


class ReplayRecorder:
    """
    Standard Replay Recorder for MatchState sequences.
    """

    def __init__(self, match_id: str, output_dir: str = "replays"):
        self.match_id = match_id
        self.output_path = os.path.join(output_dir, f"{match_id}.json")
        self.frames = []
        os.makedirs(output_dir, exist_ok=True)

    def record_frame(self, state: MatchState):
        frame = {
            "t": state.tick,
            "b": state.ball.pos.tolist(),
            "p": [{"id": p.id, "pos": p.pos.tolist(), "stm": p.stamina} for p in state.players],
            "e": [ev.event_type for ev in state.events],
        }
        self.frames.append(frame)

    def save(self, metadata: dict):
        with open(self.output_path, "w") as f:
            json.dump({"meta": metadata, "frames": self.frames}, f)
