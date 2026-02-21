import numpy as np
from typing import List, Optional, Dict
from sim.core.rng import DeterministicRNG

class SelfPlayManager:
    """
    Manages a registry of model snapshots for competitive multi-agent training.
    Enforces deterministic opponent sampling.
    """
    def __init__(self, model_pool_dir: str, rng: DeterministicRNG):
        self.model_pool_dir = model_pool_dir
        self.rng = rng
        self.sampling_probs = {"latest": 0.5, "strong": 0.3, "random": 0.2}
        self.registry: List[Dict] = [] # List of {path, elo, id}

    def add_to_pool(self, model_path: str, elo: float, model_id: str):
        self.registry.append({"path": model_path, "elo": elo, "id": model_id})

    def sample_opponent(self) -> Optional[str]:
        """Select an opponent based on the current strategy."""
        if not self.registry:
            return None
            
        r = self.rng.float()
        if r < self.sampling_probs["latest"]:
            return self.registry[-1]["path"]
        elif r < self.sampling_probs["latest"] + self.sampling_probs["strong"]:
            # Sample from top 20%
            sorted_pool = sorted(self.registry, key=lambda x: x["elo"], reverse=True)
            idx = self.rng.integers(0, max(1, len(sorted_pool) // 5))
            return sorted_pool[idx]["path"]
        else:
            idx = self.rng.integers(0, len(self.registry))
            return self.registry[idx]["path"]
