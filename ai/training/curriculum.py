class CurriculumManager:
    """
    Gated transition between training phases.
    """

    def __init__(self):
        self.phase = 0
        self.gates = [
            {"win_rate": 0.7, "min_steps": 100000},  # Phase 0 -> 1
            {"pass_accuracy": 0.5, "min_steps": 500000},  # Phase 1 -> 2
        ]

    def check_promotion(self, metrics: dict) -> bool:
        if self.phase >= len(self.gates):
            return False
        gate = self.gates[self.phase]
        for key, threshold in gate.items():
            if metrics.get(key, 0) < threshold:
                return False
        self.phase += 1
        return True
