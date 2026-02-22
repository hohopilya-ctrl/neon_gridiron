from typing import Tuple

import numpy as np


class MPCLitePlanner:
    """
    Model Predictive Control Lite.
    Simulates short-term trajectories to optimize movement targets.
    """
    def __init__(self, horizon: int = 20, dt: float = 1/60.0):
        self.horizon = horizon
        self.dt = dt

    def plan_trajectory(self, start_pos: np.ndarray, start_vel: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        """
        Simple linear-quadratic trajectory optimization toward a target.
        Returns the optimized 'next step' velocity vector.
        """
        # In a real MPC we'd solve an optimization problem.
        # Here we provide a 'lite' version: PID-like lookahead.
        lookahead_target = target_pos
        current_pos = start_pos
        current_vel = start_vel
        
        # Simple steering logic
        desired_vel = (lookahead_target - current_pos) / (self.horizon * self.dt)
        steering = desired_vel - current_vel
        
        # Return the 'planned' next velocity
        optimized_vel = current_vel + steering * 0.1
        return optimized_vel

    def predict_ball_intercept(self, ball_pos: np.ndarray, ball_vel: np.ndarray, player_pos: np.ndarray, player_max_speed: float) -> Tuple[np.ndarray, int]:
        """
        Predict where and when a player can intercept the ball.
        """
        for t in range(1, self.horizon + 50):
            # Simple linear prediction of ball
            future_ball_pos = ball_pos + ball_vel * (t * self.dt)
            # Check if player can reach that spot
            dist = np.linalg.norm(future_ball_pos - player_pos)
            if dist <= player_max_speed * (t * self.dt):
                return future_ball_pos, t
        return ball_pos, 0
