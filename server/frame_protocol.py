from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class BallFrame:
    pos: List[float]  # [x, y]
    vel: List[float]  # [vx, vy]
    spin: float = 0.0


@dataclass
class PlayerFrame:
    id: int
    team: str  # "BLUE" | "RED"
    pos: List[float]
    vel: List[float]
    stamina: float
    energy: float = 100.0
    heat: float = 0.0


@dataclass
class FrameV220:
    v: str = "2.2.0"
    tick: int = 0
    score: List[int] = field(default_factory=lambda: [0, 0])
    ball: BallFrame = field(default_factory=lambda: BallFrame([0, 0], [0, 0]))
    players: List[PlayerFrame] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)
    overlays: Dict[str, Any] = field(default_factory=dict)


def convert_legacy_to_frame(legacy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts legacy format (v2.0.0/UDP) to canonical Frame v2.2.0.
    Legacy keys: t, s, b, p, e, o
    """
    # 1. Normalize Score
    score = legacy.get("s", [0, 0])
    if isinstance(score, dict):
        score = [score.get("BLUE", 0), score.get("RED", 0)]

    # 2. Normalize Ball
    b = legacy.get("b", {})
    ball = BallFrame(pos=b.get("p", [0, 0]), vel=b.get("v", [0, 0]), spin=b.get("spin", 0.0))

    # 3. Normalize Players
    players = []
    for p in legacy.get("p", []):
        players.append(
            PlayerFrame(
                id=p.get("id", 0),
                team="BLUE" if p.get("team") == 0 else "RED",
                pos=p.get("pos", [0, 0]),
                vel=p.get("vel", [0, 0]),
                stamina=p.get("st", 100.0),
                energy=p.get("en", 100.0),
                heat=p.get("ht", 0.0),
            )
        )

    frame = FrameV220(
        tick=legacy.get("t", 0),
        score=score,
        ball=ball,
        players=players,
        events=legacy.get("e", []),
        overlays=legacy.get("o", {}),
    )

    return asdict(frame)


def normalize_frame(any_frame: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures the frame follows the v2.2.0 spec."""
    if any_frame.get("v") == "2.2.0":
        return any_frame
    return convert_legacy_to_frame(any_frame)
