import torch
import torch.nn as nn
from typing import Dict, List, Optional

class OpponentPredictor(nn.Module):
    """
    Predicts the next N steps of enemy positions based on history.
    Used for defensive positioning and intercept planning.
    """
    def __init__(self, input_dim: int = 6, hidden_dim: int = 128, predict_steps: int = 10):
        super().__init__()
        self.predict_steps = predict_steps
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.head = nn.Linear(hidden_dim, predict_steps * 2) # X, Y for each step
        
    def forward(self, enemy_history: torch.Tensor) -> torch.Tensor:
        # enemy_history: [B, num_enemies, seq_len, 6]
        B, N, S, D = enemy_history.shape
        x = enemy_history.view(B * N, S, D)
        
        _, (h_n, _) = self.lstm(x)
        out = self.head(h_n[-1]) # [B*N, predict_steps*2]
        
        return out.view(B, N, self.predict_steps, 2)
