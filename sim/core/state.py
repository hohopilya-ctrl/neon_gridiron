from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np


class TeamID(Enum):
    BLUE = 0
    RED = 1


@dataclass(frozen=True)
class PlayerConfig:
    """Static configuration for a player."""

    id: str
    name: str
    team: TeamID
    is_goalie: bool = False
    base_stamina: float = 100.0
    base_speed: float = 1.0
    base_power: float = 1.0


@dataclass
class PlayerState:
    """Mutable state of a player during a match."""

    id: str
    team: TeamID
    pos: np.ndarray = field(default_factory=lambda: np.zeros(2))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    stamina: float = 100.0
    heat: float = 0.0
    energy: float = 100.0
    active_tags: List[str] = field(default_factory=list)


@dataclass
class BallState:
    """Mutable state of the ball."""

    pos: np.ndarray = field(default_factory=lambda: np.zeros(2))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    spin: float = 0.0
    last_touch_id: Optional[str] = None
    last_touch_team: Optional[TeamID] = None


@dataclass
class MatchState:
    """Full snapshot of the simulation at a specific tick."""

    tick: int = 0
    score: Dict[TeamID, int] = field(default_factory=lambda: {TeamID.BLUE: 0, TeamID.RED: 0})
    players: List[PlayerState] = field(default_factory=list)
    ball: BallState = field(default_factory=BallState)
    events: List[Any] = field(default_factory=list)  # Replaced with MatchEvent in events.py
    spectacle_score: float = 0.0
    physics_dt: float = 1.0 / 60.0
