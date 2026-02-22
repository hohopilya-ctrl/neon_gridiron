from typing import Optional, Tuple

import numpy as np

from sim.core.state import TeamID


class RulesEngine:
    """
    Electronic referee for boundary and goal logic.
    Governs the high-level match flow (Resets, Goals, Outs).
    """

    def __init__(self, pitch_dim: Tuple[float, float]):
        self.width, self.height = pitch_dim
        self.goal_width = 80.0  # From Y=160 to Y=240
        self.goal_y_range = (
            self.height / 2 - self.goal_width / 2,
            self.height / 2 + self.goal_width / 2,
        )

    def check_goal(self, ball_pos: np.ndarray) -> Optional[TeamID]:
        """Verify if a goal event occurred."""
        x, y = ball_pos
        if self.goal_y_range[0] < y < self.goal_y_range[1]:
            if x <= 0:
                return TeamID.RED  # Blue team conceded
            if x >= self.width:
                return TeamID.BLUE  # Red team conceded
        return None

    def check_tackle(self, p1_pos: np.ndarray, p2_pos: np.ndarray) -> bool:
        """Detect if a tackle attempt is physically possible."""
        return np.linalg.norm(p1_pos - p2_pos) < 25.0

    def check_interaction(self, player_pos: np.ndarray, ball_pos: np.ndarray) -> bool:
        """Verify if player is close enough to interact with the ball."""
        return np.linalg.norm(player_pos - ball_pos) < 20.0
