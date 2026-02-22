from typing import Any, Dict

import numpy as np

from ai.env.neon_env import NeonFootballEnv


class EvalHarness:
    """
    Standardized evaluation suite for Neon agents.
    Tests agents against various scenarios (Corner, Penalty, Midfield).
    """
    def __init__(self):
        self.scenarios = [
            "standard_match",
            "corner_kick_offense",
            "penalty_defense",
            "fast_break"
        ]

    def evaluate_agent(self, env: NeonFootballEnv, agent_policy: Any, num_episodes: int = 5) -> Dict[str, float]:
        results = {}
        for scenario in self.scenarios:
            scores = []
            for _ in range(num_episodes):
                obs, _ = env.reset(options={"scenario": scenario})
                done = False
                total_reward = 0
                while not done:
                    # In a real eval, we'd use the policy
                    action = env.action_space.sample() 
                    obs, reward, terminated, truncated, info = env.step(action)
                    done = terminated or truncated
                    total_reward += reward
                scores.append(total_reward)
            results[scenario] = float(np.mean(scores))
        return results
