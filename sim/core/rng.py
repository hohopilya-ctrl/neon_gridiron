from typing import Optional

import numpy as np


class DeterministicRNG:
    """
    Unified RNG provider for the Neon Gridiron ULTRA simulation.
    Ensures that every part of the stack (Physics, AI, League) uses a single traceable seed.
    """

    def __init__(self, seed: Optional[int] = 42):
        self.seed = seed
        self.gen = np.random.default_rng(seed)

    def reset(self, seed: Optional[int] = None):
        """Reset the generator with a new or original seed."""
        if seed is not None:
            self.seed = seed
        self.gen = np.random.default_rng(self.seed)

    def float(self, low: float = 0.0, high: float = 1.0) -> float:
        return self.gen.uniform(low, high)

    def integers(self, low: int, high: Optional[int] = None) -> int:
        return self.gen.integers(low, high)

    def choice(self, items: list, p: Optional[list] = None):
        return self.gen.choice(items, p=p)

    def normal(self, loc: float = 0.0, scale: float = 1.0) -> float:
        return self.gen.normal(loc, scale)
