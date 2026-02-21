import json
from typing import Any, Dict

import msgpack

from sim.core.state import MatchState


class SimulationEncoder:
    """
    High-performance serialization for Neon Gridiron ULTRA match snapshots.
    Supports both JSON for debugging/logging and MsgPack for real-time telemetry.
    """

    @staticmethod
    def to_dict(state: MatchState) -> Dict[str, Any]:
        """Convert MatchState to a versioned flat structure."""
        return {
            "v": "2.1.0",
            "t": state.tick,
            "s": {str(k.name): v for k, v in state.score.items()},
            "b": {
                "p": state.ball.pos.tolist(),
                "v": state.ball.vel.tolist(),
                "s": round(state.ball.spin, 3),
            },
            "p": [
                {
                    "id": p.id,
                    "team": p.team.value,
                    "pos": p.pos.tolist(),
                    "vel": p.vel.tolist(),
                    "stm": round(p.stamina, 2),
                    "en": round(p.energy, 1),
                    "ht": round(p.heat, 1),
                }
                for p in state.players
            ],
            # Events truncated to type names for telemetry brevity
            "e": [e.event_type for e in state.events],
        }

    @staticmethod
    def pack(state: MatchState) -> bytes:
        return msgpack.packb(SimulationEncoder.to_dict(state), use_bin_type=True)

    @staticmethod
    def json(state: MatchState) -> str:
        return json.dumps(SimulationEncoder.to_dict(state))
