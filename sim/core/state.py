from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

class TeamID(Enum):
    BLUE = 0
    RED = 1
    SPECTATOR = 2

@dataclass(frozen=True)
class FieldConfig:
    width: float = 600.0
    height: float = 400.0
    goal_width: float = 80.0
    boundary_width: float = 5.0
    physics_dt: float = 1.0 / 60.0

@dataclass(frozen=True)
class AbilityConfig:
    dash_impulse: float = 5000.0
    dash_stamina_cost: float = 20.0
    dash_cooldown: int = 60  # ticks
    kick_power_mult: float = 1.0
    shield_duration: int = 30

@dataclass(frozen=True)
class MatchConfig:
    match_id: str
    max_ticks: int = 6000
    team_size: int = 7
    field_cfg: FieldConfig = field(default_factory=FieldConfig)
    ability_cfg: AbilityConfig = field(default_factory=AbilityConfig)

@dataclass(frozen=True)
class PlayerConfig:
    id: str
    name: str
    team: TeamID
    is_goalie: bool = False
    base_stamina: float = 100.0
    base_speed: float = 1.0
    base_power: float = 1.0

@dataclass
class PlayerState:
    id: str
    team: TeamID
    pos: np.ndarray = field(default_factory=lambda: np.zeros(2))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    stamina: float = 100.0
    heat: float = 0.0
    energy: float = 100.0
    active_tags: List[str] = field(default_factory=list)
    dash_cooldown: int = 0

@dataclass
class BallState:
    pos: np.ndarray = field(default_factory=lambda: np.zeros(2))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(2))
    spin: float = 0.0
    last_touch_id: Optional[str] = None
    last_touch_team: Optional[TeamID] = None

@dataclass
class MatchEvent:
    event_id: str
    tick: int
    event_type: str
    actor_id: Optional[str] = None
    target_id: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GoalEvent(MatchEvent):
    team_scored: TeamID = TeamID.BLUE
    event_type: str = "GOAL"

@dataclass
class PossessionEvent(MatchEvent):
    team: TeamID = TeamID.BLUE
    event_type: str = "POSSESSION"

@dataclass
class MatchState:
    tick: int = 0
    score: Dict[TeamID, int] = field(default_factory=lambda: {TeamID.BLUE: 0, TeamID.RED: 0})
    players: List[PlayerState] = field(default_factory=list)
    ball: BallState = field(default_factory=BallState)
    events: List[MatchEvent] = field(default_factory=list)
    spectacle_score: float = 0.0
    physics_dt: float = 1.0 / 60.0
    config: Optional[MatchConfig] = None
