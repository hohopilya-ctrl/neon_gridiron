from typing import Literal

ReasonCode = Literal[
    "XG_OPPORTUNITY",
    "FOUL_AVOIDANCE",
    "COACH_INTENT_FOLLOW",
    "COUNTER_ABILITY_DETECTED",
    "STAMINA_CONSERVATION",
    "MARKING_OPPONENT",
    "SPACE_CREATION",
    "EMERGENCY_SAVE",
]


class ExplainabilityFeed:
    """
    Logs decision rationale for the UI overlays.
    """

    def __init__(self):
        self.logs = []

    def log_decision(self, tick: int, agent_id: str, code: ReasonCode, weight: float):
        self.logs.append({"t": tick, "a": agent_id, "c": code, "w": weight})

    def get_summary(self, start_tick: int, end_tick: int):
        return [l for l in self.logs if start_tick <= l["t"] <= end_tick]
