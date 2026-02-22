from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import msgpack


@dataclass(frozen=True)
class TelemetryFrame:
    """
    High-performance state snapshot for UI and network sync.
    Optimized for msgpack serialization.
    """
    v: int = 2  # Protocol version
    t: int = 0  # Tick
    s: Tuple[int, int] = (0, 0)  # Score (Blue, Red)
    b: Tuple[float, float] = (0.0, 0.0)  # Ball Pos X, Y
    bv: Tuple[float, float] = (0.0, 0.0)  # Ball Vel X, Y
    p: List[Dict[str, Any]] = field(default_factory=list)  # Players: [{id, team, pos:[x,y], vel:[v,v], st, tags[]}]
    e: List[Dict[str, Any]] = field(default_factory=list)  # Events
    o: Dict[str, Any] = field(default_factory=dict) # Overlays (Explainability)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "v": self.v,
            "t": self.t,
            "s": list(self.s),
            "b": list(self.b),
            "bv": list(self.bv),
            "p": self.p,
            "e": self.e,
            "o": self.o
        }

    def pack(self) -> bytes:
        return msgpack.packb(self.to_dict(), use_bin_type=True)

    @classmethod
    def unpack(cls, data: bytes) -> TelemetryFrame:
        d = msgpack.unpackb(data, raw=False)
        return cls(
            v=d["v"],
            t=d["t"],
            s=tuple(d["s"]),
            b=tuple(d["b"]),
            bv=tuple(d["bv"]),
            p=d["p"],
            e=d["e"],
            o=d.get("o", {})
        )
