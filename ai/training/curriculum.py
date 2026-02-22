from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CurriculumGate:
    phase_name: str
    min_steps: int
    min_win_rate: float
    min_pass_accuracy: float
    min_xg_diff: float


class CurriculumManager:
    """Progressive gates for training from micro-skills to full 7v7."""

    def __init__(self):
        self.phase = 0
        self.gates: tuple[CurriculumGate, ...] = (
            CurriculumGate(
                phase_name="micro_skills",
                min_steps=100_000,
                min_win_rate=0.58,
                min_pass_accuracy=0.48,
                min_xg_diff=0.02,
            ),
            CurriculumGate(
                phase_name="small_sided",
                min_steps=300_000,
                min_win_rate=0.61,
                min_pass_accuracy=0.53,
                min_xg_diff=0.05,
            ),
            CurriculumGate(
                phase_name="full_7v7",
                min_steps=700_000,
                min_win_rate=0.65,
                min_pass_accuracy=0.58,
                min_xg_diff=0.07,
            ),
        )

    @property
    def current_phase_name(self) -> str:
        if self.phase >= len(self.gates):
            return "mastery"
        return self.gates[self.phase].phase_name

    def check_promotion(self, metrics: dict[str, float]) -> bool:
        if self.phase >= len(self.gates):
            return False

        gate = self.gates[self.phase]
        checks = (
            metrics.get("steps", 0) >= gate.min_steps,
            metrics.get("win_rate", 0.0) >= gate.min_win_rate,
            metrics.get("pass_accuracy", 0.0) >= gate.min_pass_accuracy,
            metrics.get("xg_diff", 0.0) >= gate.min_xg_diff,
        )

        if all(checks):
            self.phase += 1
            return True
        return False

    def next_targets(self) -> dict[str, float] | None:
        if self.phase >= len(self.gates):
            return None

        gate = self.gates[self.phase]
        return {
            "steps": float(gate.min_steps),
            "win_rate": gate.min_win_rate,
            "pass_accuracy": gate.min_pass_accuracy,
            "xg_diff": gate.min_xg_diff,
        }
