import numpy as np

class SelfPlayManager:
    """
    Manages the pool of opponent snapshots for competitive training.
    """

    def __init__(self, registry, rng=None, seed=42):
        self.registry = registry
        self.rng = rng if rng is not None else np.random.default_rng(seed)
        self.sampling_probs = {"latest": 0.6, "strong": 0.2, "weak": 0.2}

    def sample_opponent(self) -> str:
        r = self.rng.random()
        if r < self.sampling_probs["latest"]:
            return self.registry.get_latest()
        elif r < self.sampling_probs["latest"] + self.sampling_probs["strong"]:
            return self.registry.get_top_percentile(20)
        else:
            return self.registry.get_random_past()
