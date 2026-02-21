from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
from typing import List, Optional, Dict

class EventType(Enum):
    MATCH_START = auto()
    MATCH_END = auto()
    GOAL = auto()
    FOUL = auto()
    KICK = auto()
    DASH = auto()
    ABILITY_USE = auto()
    STAMINA_DEPLETED = auto()

@dataclass(frozen=True)
class GameEvent:
    tick: int
    event_type: EventType
    team_id: Optional[int] = None
    player_id: Optional[str] = None
    pos: Optional[np.ndarray] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class PlayerState:
    id: str
    team: int
    pos: np.ndarray = field(default_factory=lambda: np.zeros(2))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    stamina: float = 100.0
    is_goalie: bool = False
    is_dashing: bool = False
    active_tags: List[str] = field(default_factory=list)

@dataclass
class BallState:
    pos: np.ndarray = field(default_factory=lambda: np.zeros(2))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    spin: float = 0.0

@dataclass
class MatchState:
    tick: int = 0
    score: List[int] = field(default_factory=lambda: [0, 0])
    players: List[PlayerState] = field(default_factory=list)
    ball: BallState = field(default_factory=BallState)
    events: List[GameEvent] = field(default_factory=list)
    spectacle_score: float = 0.0
# lines: 25
