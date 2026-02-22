from typing import Any, Dict, List

import numpy as np

from sim.core.state import TeamID


class RewardShaper:
    """
    Advanced Meta-Reward Shaper for ULTRA Phase 2.
    Combines sparse goals with dense hierarchical metrics.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.cfg = config or {}
        self.w_goal = self.cfg.get("w_goal", 10.0)
        self.w_ball_dist = self.cfg.get("w_ball_dist", 0.01)
        self.w_possession = self.cfg.get("w_possession", 0.1)
        self.w_spectacle = self.cfg.get("w_spectacle", 0.05)

    def compute_meta_reward(self, state: Any, events: List[Any]) -> Dict[str, float]:
        rewards = {"total": 0.0, "goal": 0.0, "dense": 0.0, "spec": 0.0}

        # 1. Sparse Goal Rewards
        for ev in events:
            if getattr(ev, "event_type", None) == "GOAL":
                rewards["goal"] += self.w_goal

        # 2. Dense Ball Proximity (distance from closest player to the ball)
        if getattr(state, "players", None):
            ball_pos = np.asarray(state.ball.pos, dtype=np.float32)
            min_dist = min(float(np.linalg.norm(np.asarray(p.pos) - ball_pos)) for p in state.players)
            rewards["dense"] += self.w_ball_dist * (1.0 / (1.0 + min_dist / 100.0))

        # 3. Possession Reward
        if getattr(state.ball, "last_touch_team", None) == TeamID.BLUE:
            rewards["dense"] += self.w_possession

        # 4. Spectacle Score
        rewards["spec"] += float(getattr(state, "spectacle_score", 0.0)) * self.w_spectacle

        rewards["total"] = rewards["goal"] + rewards["dense"] + rewards["spec"]
        return rewards
