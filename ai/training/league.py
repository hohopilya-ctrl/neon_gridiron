import json
import time
from pathlib import Path
from typing import Dict

from ai.env.neon_env import NeonFootballEnv
from ai.training.self_play import SelfPlayManager
from sim.core.rng import DeterministicRNG
from sim.core.state import TeamID


class EloSystem:
    def __init__(self, k_factor: float = 32.0):
        self.k = k_factor

    def calculate_new_ratings(self, player_elo: float, opponent_elo: float, result: float) -> float:
        """result: 1.0 for win, 0.5 for draw, 0.0 for loss."""
        expected = 1.0 / (1.0 + 10 ** ((opponent_elo - player_elo) / 400.0))
        return player_elo + self.k * (result - expected)


class LeagueEngine:
    """
    High-level manager for concurrent training and evaluation.
    Tracks agent strength (Elo) and manages the competitive evolution.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.rng = DeterministicRNG(seed=config.get("seed", 42))
        self.self_play = SelfPlayManager("models/pool", self.rng)
        self.elo = EloSystem()

        self.model_metadata: Dict[str, Dict] = {}
        self._load_registry()

    def _load_registry(self):
        pool_path = Path("models/pool")
        pool_path.mkdir(parents=True, exist_ok=True)
        # Load existing .json metadata files

    def run_evaluation(self, learner, opponent_path: str, num_episodes: int = 5) -> float:
        """Evaluate learner against a specific snapshot."""
        env = NeonFootballEnv({"seed": self.rng.integers(0, 1000000)})
        total_score = 0.0

        for _ in range(num_episodes):
            obs, _ = env.reset()
            done = False
            while not done:
                # Placeholder: Both teams same policy or heuristic
                action, _ = learner.predict(obs)
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated

            final_score = env.state.score
            if final_score[TeamID.BLUE] > final_score[TeamID.RED]:
                total_score += 1.0
            elif final_score[TeamID.BLUE] == final_score[TeamID.RED]:
                total_score += 0.5

        return total_score / num_episodes

    def save_snapshot(self, model, name: str, current_elo: float):
        path = f"models/pool/{name}.zip"
        meta_path = f"models/pool/{name}.json"

        model.save(path)
        with open(meta_path, "w") as f:
            json.dump(
                {"name": name, "elo": current_elo, "timestamp": time.time(), "metrics": {}}, f
            )

        self.self_play.add_to_pool(path, current_elo, name)
        print(f"🏆 League: New snapshot {name} saved with Elo {current_elo:.0f}")
