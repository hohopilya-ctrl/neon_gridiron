import numpy as np
from typing import Dict, Any, Optional
from sim.core.state import MatchState, TeamID

class RewardShaper:
    """
    Advanced reward shaping for Neon Gridiron ULTRA.
    Balances completion of objectives with auxiliary shaping for faster convergence.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            "goal_reward": 10.0,
            "ball_dist_coeff": 0.01,
            "possession_bonus": 0.05,
            "spectacle_bonus": 0.1
        }

    def compute(self, state: MatchState, goal_team: Optional[TeamID]) -> float:
        reward = 0.0
        
        # 1. Sparse Goal Reward
        if goal_team == TeamID.BLUE:
            reward += self.config["goal_reward"]
        elif goal_team == TeamID.RED:
            reward -= self.config["goal_reward"]
            
        # 2. Ball Proximity (Encourage offensive pressure)
        # We find the closest player to the ball
        ball_pos = state.ball.pos
        min_dist = float('inf')
        for p in state.players:
            if p.team == TeamID.BLUE:
                dist = np.linalg.norm(ball_pos - p.pos)
                if dist < min_dist:
                    min_dist = dist
        
        reward += self.config["ball_dist_coeff"] * (1.0 / (1.0 + min_dist / 100.0))
        
        # 3. Possession Reward
        if state.ball.last_touch_team == TeamID.BLUE:
            reward += self.config["possession_bonus"]
            
        # 4. Spectacle Score (Energy conservation vs Movement)
        reward += state.spectacle_score * self.config["spectacle_bonus"]
        
        return float(reward)
