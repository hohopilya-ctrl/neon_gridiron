from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Literal

EventType = Literal[
    "KICKOFF","PASS","SHOT","GOAL","SAVE","TACKLE","INTERCEPT",
    "FOUL","YELLOW","RED","PENALTY","CORNER","THROW_IN",
    "ABILITY_CAST","ADVANTAGE_START","ADVANTAGE_END","VAR_CHECK",
    "TIME_WASTING_FLAG","OFFSIDE","HALF_END"
]

@dataclass(frozen=True)
class MatchEvent:
    event_id: str
    tick: int
    event_type: EventType
    actor_id: str
    target_id: Optional[str] = None
    team_id: Optional[str] = None
    zone: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
# lines: 25
