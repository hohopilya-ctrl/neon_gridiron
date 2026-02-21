from typing import List, Dict, Optional
import numpy as np
from sim.core.state import PlayerState, TeamID
from sim.core.events import MatchEvent

class Referee:
    """
    Manages fair play, fouls, and penalty cards.
    Tracks player aggression and enforces discipline.
    """
    def __init__(self, foul_threshold: float = 15.0):
        self.foul_threshold = foul_threshold
        self.penalty_points: Dict[str, float] = {} # player_id -> cumulative_points
        self.cards: Dict[str, List[str]] = {} # player_id -> ["YELLOW", "RED"]

    def process_collision(self, actor_id: str, target_id: str, impulse: float, tick: int) -> List[MatchEvent]:
        """Analyze a physical collision for foul potential."""
        events = []
        if impulse > self.foul_threshold:
            # Calculate penalty logic (e.g., from collision severity)
            points = (impulse - self.foul_threshold) / 2.0
            self.penalty_points[actor_id] = self.penalty_points.get(actor_id, 0.0) + points
            
            events.append(MatchEvent(
                event_id=f"foul_{tick}_{actor_id}",
                tick=tick,
                event_type="FOUL",
                actor_id=actor_id,
                target_id=target_id,
                params={"severity": impulse}
            ))

            # Disciplinary checks
            cumulative = self.penalty_points[actor_id]
            if cumulative > 40.0 and actor_id not in self.cards:
                self.cards[actor_id] = ["YELLOW"]
                events.append(MatchEvent(f"y_{tick}", tick, "YELLOW", actor_id))
            elif cumulative > 100.0 and "RED" not in self.cards.get(actor_id, []):
                self.cards.setdefault(actor_id, []).append("RED")
                events.append(MatchEvent(f"r_{tick}", tick, "RED", actor_id))
                
        return events
