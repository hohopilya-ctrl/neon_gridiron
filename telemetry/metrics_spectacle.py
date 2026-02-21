class SpectacleAuditor:
    """
    Calculates how 'TV-ready' or exciting the match is.
    """

    def __init__(self, config: dict):
        self.w = config.get("weights", {"goal": 10, "save": 5, "long_pass": 2})

    def compute_score(self, events: list) -> float:
        score = 0.0
        for ev in events:
            score += self.w.get(ev.event_type.lower(), 0)
        return score
