import numpy as np
from typing import Optional, Tuple
from sim.core.state import TeamID

class RulesEngine:
    """
    Electronic referee for boundary and goal logic.
    Governs the high-level match flow (Resets, Goals, Outs).
    """
    def __init__(self, pitch_dim: Tuple[float, float]):
        self.width, self.height = pitch_dim
        self.goal_width = 80.0 # From Y=160 to Y=240
        self.goal_y_range = (self.height/2 - self.goal_width/2, self.height/2 + self.goal_width/2)

    def check_goal(self, ball_pos: np.ndarray) -> Optional[TeamID]:
        """Verify if a goal event occurred."""
        x, y = ball_pos
        if self.goal_y_range[0] < y < self.goal_y_range[1]:
            if x <= 0:
                return TeamID.RED # Blue team conceded
            if x >= self.width:
                return TeamID.BLUE # Red team conceded
        return None

    def check_out_of_bounds(self, ball_pos: np.ndarray) -> Optional[str]:
        """Detect ball exiting the field (Corner, Throw-in, Goal Kick)."""
        x, y = ball_pos
        if x < 0 or x > self.width or y < 0 or y > self.height:
            if self.goal_y_range[0] < y < self.goal_y_range[1]:
                return None # It's a goal check, handled elsewhere
            return "OUT_OF_BOUNDS"
        return None
