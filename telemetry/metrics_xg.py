from typing import List

import numpy as np


def calculate_xg(
    ball_pos: np.ndarray, goal_pos: np.ndarray, defenders: List[np.ndarray], angle_bonus: float
) -> float:
    """
    Advanced Expected Goals (xG) calculation.
    """
    dist = np.linalg.norm(ball_pos - goal_pos)
    angle = 1.0  # Placeholder for angle-to-goal calculation

    # xG decreases with distance and increases with better angle
    base_xg = np.exp(-0.05 * dist) * angle * angle_bonus

    # Apply defender pressure penalty
    for d_pos in defenders:
        if np.linalg.norm(ball_pos - d_pos) < 2.0:
            base_xg *= 0.8

    return float(np.clip(base_xg, 0.01, 0.99))
