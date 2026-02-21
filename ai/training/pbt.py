import copy
import random
from typing import List


class PBTManager:
    """
    Population Based Training: Exploit and Explore.
    """

    def __init__(self, population_size: int = 16):
        self.pop_size = population_size
        self.population = []  # List of config dicts

    def exploit_and_explore(self, top_performers: List[dict]):
        new_population = []
        for _ in range(self.pop_size):
            # Exploit: copy a top performer
            parent = copy.deepcopy(random.choice(top_performers))

            # Explore: mutate sensitive parameters
            parent["reward_weights"]["goal"] *= random.uniform(0.8, 1.2)
            if "ability_pref" in parent:
                parent["ability_pref"]["dash_bias"] += random.uniform(-0.1, 0.1)

            new_population.append(parent)
        return new_population
