from typing import List, Dict
from sim.core.events import MatchEvent
from sim.core.state import MatchState


class Referee:
    """
    Manages fouls, penalty points, and cards using MatchEvent protocol.
    """

    def __init__(self, config: dict):
        self.config = config
        self.foul_threshold = config.get("foul_threshold", 10.0)
        self.penalty_history = {}  # actor_id -> points

    def process_collision(
        self, actor_id: str, target_id: str, impulse: float, tick: int
    ) -> List[MatchEvent]:
        events = []
        if impulse > self.foul_threshold:
            self.penalty_history[actor_id] = self.penalty_history.get(actor_id, 0) + (
                impulse / 10.0
            )
            events.append(
                MatchEvent(
                    event_id=f"foul_{tick}_{actor_id}",
                    tick=tick,
                    event_type="FOUL",
                    actor_id=actor_id,
                    target_id=target_id,
                    params={"severity": impulse},
                )
            )

            # Card logic
            score = self.penalty_history[actor_id]
            if score > 50 and score < 100:
                events.append(MatchEvent(f"y_{tick}", tick, "YELLOW", actor_id))
            elif score >= 100:
                events.append(MatchEvent(f"r_{tick}", tick, "RED", actor_id))

        return events

    def check_var(self, event: MatchEvent) -> bool:
        """Probabilistic VAR check for high-stakes fouls."""
        return event.event_type == "FOUL" and event.params.get("severity", 0) > 30.0
