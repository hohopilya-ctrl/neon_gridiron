import numpy as np
from typing import Optional, Tuple


class RulesEngine:
    def __init__(self, pitch_dim: Tuple[float, float]):
        self.width, self.height = pitch_dim

    def check_out_of_bounds(self, ball_pos: np.ndarray) -> Optional[str]:
        if ball_pos[0] < 0 or ball_pos[0] > self.width:
            return "THROW_IN" if 5 < ball_pos[1] < self.height - 5 else "GOAL_KICK"
        if ball_pos[1] < 0 or ball_pos[1] > self.height:
            return "THROW_IN"
        return None

    def check_goal(self, ball_pos: np.ndarray) -> Optional[int]:
        if (ball_pos[0] < 0 or ball_pos[0] > self.width) and (
            self.height / 2 - 4 < ball_pos[1] < self.height / 2 + 4
        ):
            return 0 if ball_pos[0] > self.width else 1
        return None
