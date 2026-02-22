class CurriculumManager:
    """
    Gated transition between training phases for 7v7 Football.
    """
    STAGE_SKILLS = 0    # Focus on ball touch & basic movement
    STAGE_TACTICS = 1   # Focus on passing & positioning (3v3 / 5v5)
    STAGE_MASTERY = 2   # Full 7v7 tactical play

    def __init__(self):
        self.phase = self.STAGE_SKILLS
        self.gates = [
            {"goal_rate": 0.5, "min_steps": 50000},    # Phase 0 -> 1
            {"pass_accuracy": 0.6, "min_steps": 200000}, # Phase 1 -> 2
        ]

    def get_phase_config(self) -> dict:
        """Return env/reward settings for current phase."""
        if self.phase == self.STAGE_SKILLS:
            return {"max_players": 2, "ball_impulse_boost": 1.5, "reward_profile": "attacking"}
        if self.phase == self.STAGE_TACTICS:
            return {"max_players": 10, "ball_impulse_boost": 1.0, "reward_profile": "balanced"}
        return {"max_players": 14, "ball_impulse_boost": 1.0, "reward_profile": "league"}

    def check_promotion(self, metrics: dict) -> bool:
        if self.phase >= len(self.gates):
            return False
        gate = self.gates[self.phase]
        for key, threshold in gate.items():
            if metrics.get(key, 0) < threshold:
                return False
        self.phase += 1
        return True
