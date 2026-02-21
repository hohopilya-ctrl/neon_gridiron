import json
import msgpack
import numpy as np
from typing import Any, Dict, Optional
from sim.core.state import MatchState, GameEvent, PlayerState, BallState

class SimulationEncoder:
    """Handles professional serialization of simulation state and events."""
    
    @staticmethod
    def to_dict(state: MatchState) -> Dict[str, Any]:
        """Convert MatchState to a JSON-serializable dictionary."""
        return {
            "v": "2.0.0",
            "t": state.tick,
            "s": state.score,
            "b": {
                "p": state.ball.pos.tolist(),
                "v": state.ball.vel.tolist(),
                "s": state.ball.spin
            },
            "p": [
                {
                    "id": p.id,
                    "t": p.team,
                    "p": p.pos.tolist(),
                    "v": p.vel.tolist(),
                    "stm": round(p.stamina, 2)
                } for p in state.players
            ],
            "e": [
                {
                    "t": e.event_type.name,
                    "tid": e.team_id,
                    "pid": e.player_id,
                    "meta": e.metadata
                } for e in state.events
            ]
        }

    @staticmethod
    def encode_msgpack(state: MatchState) -> bytes:
        """High-performance binary encoding for telemetry."""
        return msgpack.packb(SimulationEncoder.to_dict(state), use_bin_type=True)

    @staticmethod
    def encode_json(state: MatchState) -> str:
        """Standard JSON encoding."""
        return json.dumps(SimulationEncoder.to_dict(state))

class SimulationRecorder:
    """Professional streamable replay recorder using JSONL."""
    def __init__(self, path: str):
        self.path = path
        self.file = None

    def start(self):
        self.file = open(self.path, 'w')

    def record_frame(self, state: MatchState):
        if self.file and state:
            data = SimulationEncoder.to_dict(state)
            self.file.write(json.dumps(data) + "\n")

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None
