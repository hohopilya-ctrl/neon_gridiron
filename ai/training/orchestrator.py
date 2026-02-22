from typing import Any, Dict, List

import torch
import torch.optim as optim

from ai.models.policy import ActorCritic
from ai.training.curiosity import IntrinsicCuriosityModule
from ai.training.league import LeagueManager
from ai.training.rewards import RewardShaper


class PBTTrainer:
    """
    ULTRA Orchestrator: Population-Based Training + League Integration.
    Manages the lifecycle of multiple competing agent populations.
    """
    def __init__(self, num_agents: int = 16, device: str = "cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.population = [ActorCritic(embed_dim=128).to(self.device) for _ in range(num_agents)]
        self.optimizers = [optim.Adam(p.parameters(), lr=3e-4) for p in self.population]
        self.icms = [IntrinsicCuriosityModule(state_dim=128, action_dim=8).to(self.device) for _ in range(num_agents)]
        
        self.league = LeagueManager()
        self.shaper = RewardShaper()
        self.generation = 0

    def step_generation(self, trajectories: List[Dict[str, Any]]):
        """
        One generation of PBT (Exploit & Explore).
        """
        self.generation += 1
        fitness_scores = self._evaluate_population(trajectories)
        
        # Sort by fitness
        indexed_fitness = sorted(enumerate(fitness_scores), key=lambda x: x[1], reverse=True)
        
        # Exploit: Replace bottom 25% with top 25%
        num_replace = len(self.population) // 4
        for i in range(num_replace):
            winner_idx = indexed_fitness[i][0]
            loser_idx = indexed_fitness[-(i+1)][0]
            self._copy_agent(winner_idx, loser_idx)
            self._perturb_agent(loser_idx)
            
        print(f"PBT Generation {self.generation}: Mean Fitness {sum(fitness_scores)/len(fitness_scores):.2f}")

    def _evaluate_population(self, trajectories: List[Dict[str, Any]]) -> List[float]:
        # Logic to compute mean reward per agent from trajectories
        return [sum(t['rewards']) for t in trajectories]

    def _copy_agent(self, src: int, dst: int):
        self.population[dst].load_state_dict(self.population[src].state_dict())
        self.icms[dst].load_state_dict(self.icms[src].state_dict())

    def _perturb_agent(self, idx: int):
        # Mutate learning rate or model noise for exploration
        for param_group in self.optimizers[idx].param_groups:
            param_group['lr'] *= 1.1 if torch.rand(1) > 0.5 else 0.9
