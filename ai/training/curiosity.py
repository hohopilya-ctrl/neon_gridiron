import torch
import torch.nn as nn
import torch.nn.functional as F


class IntrinsicCuriosityModule(nn.Module):
    """
    Implements Curiosity-driven exploration (Pathak et al.).
    Encourages agents to visit states that are hard to predict.
    """

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        # 1. Feature encoder for the state
        self.feature_net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim), nn.LeakyReLU(), nn.Linear(hidden_dim, hidden_dim)
        )

        # 2. Forward model: predicts next state features from current (state_feat, action)
        self.forward_model = nn.Sequential(
            nn.Linear(hidden_dim + action_dim, hidden_dim),
            nn.LeakyReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # 3. Inverse model: predicts action from (state_feat, next_state_feat)
        self.inverse_model = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim), nn.LeakyReLU(), nn.Linear(hidden_dim, action_dim)
        )

    def forward(self, state, next_state, action):
        # state, next_state: [B, D], action: [B, A]
        phi_t = self.feature_net(state)
        phi_t_plus_1 = self.feature_net(next_state)

        # Inverse prediction
        pred_action = self.inverse_model(torch.cat([phi_t, phi_t_plus_1], dim=-1))
        inv_loss = F.mse_loss(pred_action, action)

        # Forward prediction
        pred_phi_t_plus_1 = self.forward_model(torch.cat([phi_t, action], dim=-1))
        fwd_loss = F.mse_loss(pred_phi_t_plus_1, phi_t_plus_1.detach())

        # Curiosity reward is the forward prediction error
        curiosity_reward = 0.5 * torch.sum((pred_phi_t_plus_1 - phi_t_plus_1.detach()) ** 2, dim=-1)

        return curiosity_reward, inv_loss, fwd_loss
