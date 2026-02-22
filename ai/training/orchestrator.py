from typing import Any, Dict, List

import torch
import torch.optim as optim

import torch.nn.functional as F
from ai.models.policy import ActorCritic
from ai.training.league import LeagueManager


from ai.training.curriculum import CurriculumManager

class PBTTrainer:
    """
    ULTRA Orchestrator: PPO + PBT + Curriculum.
    """
    def __init__(self, num_agents: int = 4, device: str = "cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        # embed_dim matches Phase 3 architecture
        self.population = [ActorCritic(embed_dim=256).to(self.device) for _ in range(num_agents)]
        self.optimizers = [optim.Adam(p.parameters(), lr=1e-4) for p in self.population]
        
        self.curriculum = CurriculumManager()
        self.league = LeagueManager()
        self.generation = 0
        self.total_steps = 0

    def update_ppo(self, agent_idx: int, batch: Dict[str, torch.Tensor]):
        """Standard PPO update for a specific agent in the population."""
        agent = self.population[agent_idx]
        optimizer = self.optimizers[agent_idx]
        
        # Policy & Value update
        out = agent(batch['obs'])
        obs_mean, obs_std = out['mean'], out['std']
        values = out['value']
        
        # Current Log Probs
        dist = torch.distributions.Normal(obs_mean, obs_std)
        log_probs = dist.log_prob(batch['actions']).sum(-1, keepdim=True)
        entropy = dist.entropy().mean()
        
        # PPO Clipping
        ratio = torch.exp(log_probs - batch['old_log_probs'])
        surr1 = ratio * batch['advantages']
        surr2 = torch.clamp(ratio, 0.8, 1.2) * batch['advantages']
        policy_loss = -torch.min(surr1, surr2).mean()
        
        # Value Loss
        value_loss = F.mse_loss(values, batch['returns'])
        
        # Total Loss with Entropy Bonus
        loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
        
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(agent.parameters(), 1.0)
        optimizer.step()
        
        return {"policy_loss": policy_loss.item(), "value_loss": value_loss.item()}

    def step_generation(self, metrics: Dict[str, float]):
        self.generation += 1
        
        # Check for Phase promotion
        if self.curriculum.check_promotion(metrics):
            print(f"CURRICULUM UPGRADE: Entering Phase {self.curriculum.phase}")
            
        # PBT Logic
        # (Fitness evaluation and copy/perturb)
