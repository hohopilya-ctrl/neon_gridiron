import numpy as np
from typing import List, Dict, Any, Optional
from sim.core.state import MatchState, TeamID

class RewardShaper:
    """
    Advanced Meta-Reward Shaper for ULTRA Phase 2.
    Combines sparse goals with dense hierarchical metrics.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.cfg = config or {}
        self.w_goal = self.cfg.get("w_goal", 10.0)
        self.w_ball_dist = self.cfg.get("w_ball_dist", 0.01)
        self.w_possession = self.cfg.get("w_possession", 0.1)
        self.w_spectacle = self.cfg.get("w_spectacle", 0.05)
        self.w_coordination = self.cfg.get("w_coordination", 0.02)

    def compute_meta_reward(self, state: Any, events: List[Any]) -> Dict[str, float]:
        rewards = {"total": 0.0, "goal": 0.0, "dense": 0.0, "spec": 0.0}
        
        # 1. Sparse Goal Rewards
        for ev in events:
            if ev.event_type == "GOAL":
                rewards["goal"] += self.w_goal
                
        # 2. Dense Ball Proximity (Multi-agent sum)
        ball_pos = state.ball.pos
        avg_dist = 0
        for p in state.players:
                    min_dist = dist
        
        reward += self.config["ball_dist_coeff"] * (1.0 / (1.0 + min_dist / 100.0))
        
        # 3. Possession Reward
        if state.ball.last_touch_team == TeamID.BLUE:
            reward += self.config["possession_bonus"]
            
        # 4. Spectacle Score (Energy conservation vs Movement)
        reward += state.spectacle_score * self.config["spectacle_bonus"]
        
        return float(reward)
