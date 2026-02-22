from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from sim.core.state import TeamID


@dataclass(frozen=True)
class FormationLayout:
    name: str
    blue_slots: tuple[tuple[float, float], ...]
    red_slots: tuple[tuple[float, float], ...]


DEFAULT_2_3_1 = FormationLayout(
    name="2-3-1",
    blue_slots=(
        (36.0, 200.0),
        (126.0, 120.0),
        (126.0, 280.0),
        (240.0, 95.0),
        (240.0, 200.0),
        (240.0, 305.0),
        (396.0, 200.0),
    ),
    red_slots=(
        (564.0, 200.0),
        (474.0, 120.0),
        (474.0, 280.0),
        (360.0, 95.0),
        (360.0, 200.0),
        (360.0, 305.0),
        (204.0, 200.0),
    ),
)


class FormationPlanner:
    """Compute role anchors and movement targets based on game phase."""

    def __init__(self, layout: FormationLayout = DEFAULT_2_3_1):
        self.layout = layout

    def anchors_for_team(self, team: TeamID) -> np.ndarray:
        slots = self.layout.blue_slots if team is TeamID.BLUE else self.layout.red_slots
        return np.asarray(slots, dtype=np.float32)

    def shifted_targets(
        self,
        team: TeamID,
        ball_pos: np.ndarray,
        possession_team: TeamID | None,
    ) -> np.ndarray:
        anchors = self.anchors_for_team(team)

        # Team with possession stretches; defending team compacts.
        if possession_team is team:
            x_shift = np.clip((ball_pos[0] - 300.0) * 0.12, -52.0, 52.0)
            y_shift = np.clip((ball_pos[1] - 200.0) * 0.08, -28.0, 28.0)
            scale = 1.08
        else:
            x_shift = np.clip((ball_pos[0] - 300.0) * 0.07, -34.0, 34.0)
            y_shift = np.clip((ball_pos[1] - 200.0) * 0.05, -20.0, 20.0)
            scale = 0.94

        centered = anchors - np.array([300.0, 200.0], dtype=np.float32)
        shifted = centered * scale + np.array([300.0 + x_shift, 200.0 + y_shift], dtype=np.float32)
        shifted[:, 0] = np.clip(shifted[:, 0], 0.0, 600.0)
        shifted[:, 1] = np.clip(shifted[:, 1], 0.0, 400.0)
        return shifted

    def spacing_score(self, team_positions: np.ndarray) -> float:
        if team_positions.shape[0] < 2:
            return 0.0

        pairwise = []
        for i in range(team_positions.shape[0]):
            for j in range(i + 1, team_positions.shape[0]):
                pairwise.append(np.linalg.norm(team_positions[i] - team_positions[j]))

        mean_dist = float(np.mean(pairwise))
        return float(np.clip(mean_dist / 160.0, 0.0, 1.0))
