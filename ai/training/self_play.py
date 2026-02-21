# OUTPUT PART 4/Y
# Neon Gridiron ULTRA: Training Pipeline (Self-Play, League, PBT)

# File: ai/training/self_play.py
import random
from typing import List, Tuple
from ai.training.checkpoints import ModelRegistry

class SelfPlayManager:
    """
    Manages the pool of opponent snapshots for competitive training.
    """
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.sampling_probs = {
            "latest": 0.6,
            "strong": 0.2,
            "weak": 0.2
        }

    def sample_opponent(self) -> str:
        r = random.random()
        if r < self.sampling_probs["latest"]:
            return self.registry.get_latest()
        elif r < self.sampling_probs["latest"] + self.sampling_probs["strong"]:
            return self.registry.get_top_percentile(20)
        else:
            return self.registry.get_random_past()
# lines: 25

# File: ai/training/league.py
import numpy as np

class LeagueMatchmaker:
    """
    Handles Elo/Glicko ratings and matchmaking for the agent population.
    """
    def __init__(self, k_factor: int = 32):
        self.ratings = {} # model_id -> float
        self.k_factor = k_factor

    def update_ratings(self, model_a: str, model_b: str, score_a: float):
        # score_a: 1.0 for win, 0.5 for draw, 0.0 for loss
        ra = self.ratings.get(model_a, 1200.0)
        rb = self.ratings.get(model_b, 1200.0)
        
        expected_a = 1.0 / (1.0 + 10**((rb - ra) / 400.0))
        new_ra = ra + self.k_factor * (score_a - expected_a)
        
        self.ratings[model_a] = new_ra
        # Symmetric update for rb...
# lines: 20

# File: ai/training/pbt.py
import copy
import random

class PBTManager:
    """
    Population Based Training: Exploit and Explore.
    """
    def __init__(self, population_size: int = 16):
        self.pop_size = population_size
        self.population = [] # List of config dicts

    def exploit_and_explore(self, top_performers: List[dict]):
        new_population = []
        for _ in range(self.pop_size):
            # Exploit: copy a top performer
            parent = copy.deepcopy(random.choice(top_performers))
            
            # Explore: mutate sensitive parameters (Phase 17.2 traits)
            parent['reward_weights']['goal'] *= random.uniform(0.8, 1.2)
            parent['ability_pref']['dash_bias'] += random.uniform(-0.1, 0.1)
            
            new_population.append(parent)
        return new_population
# lines: 25

# File: ai/training/curriculum.py
class CurriculumManager:
    """
    Gated transition between training phases.
    """
    def __init__(self):
        self.phase = 0
        self.gates = [
            {"win_rate": 0.7, "min_steps": 100000}, # Phase 0 -> 1
            {"pass_accuracy": 0.5, "min_steps": 500000} # Phase 1 -> 2
        ]

    def check_promotion(self, metrics: dict) -> bool:
        if self.phase >= len(self.gates): return False
        gate = self.gates[self.phase]
        for key, threshold in gate.items():
            if metrics.get(key, 0) < threshold:
                return False
        self.phase += 1
        return True
# lines: 20

# END OF PART 4 - to continue output next part.
