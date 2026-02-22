import torch
import torch.nn.functional as F
import torch.optim as optim

from ai.models.policy import ActorCritic
from ai.models.world_model import WorldModel


class DreamerTrainer:
    """
    ULTRA Dreamer Orchestrator.
    Trains a world model and then trains a policy in the imagined states.
    """

    def __init__(self, obs_dim: int, action_dim: int, device: str = "cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")

        self.world_model = WorldModel(obs_dim, action_dim).to(self.device)
        self.policy = ActorCritic(embed_dim=128).to(self.device)

        self.wm_optimizer = optim.Adam(self.world_model.parameters(), lr=3e-4)
        self.policy_optimizer = optim.Adam(self.policy.parameters(), lr=1e-4)

        self.horizon = 15  # Imagination horizon

    def train_world_model(self, obs: torch.Tensor, actions: torch.Tensor, rewards: torch.Tensor):
        """
        Train the world model on real data.
        """
        self.wm_optimizer.zero_grad()

        # We assume batch of sequences [B, T, D]
        # (Simplified for single-step for demo depth)
        prev_state = None
        loss = 0

        # Loop through sequence
        for t in range(obs.shape[1] - 1):
            state, recon_obs, pred_reward, stats = self.world_model(obs[:, t], actions[:, t], prev_state)

            # Reconstruction loss
            recon_loss = F.mse_loss(recon_obs, obs[:, t])
            # Reward prediction loss
            reward_loss = F.mse_loss(pred_reward, rewards[:, t])
            # KL Divergence for latent space bottleneck
            kl_loss = self._kl_divergence(stats)

            loss += recon_loss + reward_loss + 0.1 * kl_loss
            prev_state = state

        loss.backward()
        self.wm_optimizer.step()
        return loss.item()

    def train_policy_in_imagination(self, start_obs: torch.Tensor):
        """
        Train the actor-critic in the imagined world.
        """
        self.policy_optimizer.zero_grad()

        # Start from a real observation and encode to latent
        state, _, _, _ = self.world_model(start_obs, torch.zeros(start_obs.shape[0], 2).to(self.device))

        imagined_rewards = []

        # Imagine horizon steps
        for _ in range(self.horizon):
            # 1. Policy chooses action
            # (Simplified latent input)
            latent = torch.cat(state, dim=-1)
            action_logits, _, _ = self.policy.actor_backbone(latent)
            action = torch.tanh(action_logits)  # Continuous action

            # 2. World model predicts next state
            state, _, reward, _ = self.world_model.rssm.imagine(action, state)
            imagined_rewards.append(reward)

        # 3. Compute value targets and update policy
        # (Simplified RL update)
        loss = -torch.stack(imagined_rewards).sum()  # Maximize reward
        loss.backward()
        self.policy_optimizer.step()

        return loss.item()

    def _kl_divergence(self, stats):
        mean, std = stats
        return -0.5 * torch.sum(1 + torch.log(std**2) - mean**2 - std**2, dim=-1).mean()
