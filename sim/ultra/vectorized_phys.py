from typing import Dict

import torch


class VectorizedNeonPhysics:
    """
    ULTRA Vectorized Physics Engine.
    Simulates N parallel environments using PyTorch tensors.
    Optimized for CUDA performance.
    """
    def __init__(self, num_envs: int, device: str = "cuda"):
        self.num_envs = num_envs
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        
        # Grid boundaries
        self.field_width = 60.0
        self.field_height = 40.0
        
        # State tensors: [N, num_entities, 2] (pos) and [N, num_entities, 2] (vel)
        # Entity 0: Ball, Entities 1-7: Team Blue, Entities 8-14: Team Red
        self.pos = torch.zeros((num_envs, 15, 2), device=self.device)
        self.vel = torch.zeros((num_envs, 15, 2), device=self.device)
        self.mass = torch.ones((15,), device=self.device)
        self.mass[0] = 0.5 # Ball is lighter
        
        self.friction = 0.98
        self.dt = 1/60.0

    def reset(self, indices: torch.Tensor = None):
        if indices is None:
            indices = torch.arange(self.num_envs, device=self.device)
            
        # Randomize ball
        self.pos[indices, 0] = torch.rand((len(indices), 2), device=self.device) * 10 - 5
        self.vel[indices, 0] = 0
        
        # Reset players to formation
        # (Simplified for now: random scatter)
        self.pos[indices, 1:] = torch.randn((len(indices), 14, 2), device=self.device) * 5
        self.vel[indices, 1:] = 0

    def step(self, actions: torch.Tensor):
        """
        actions: [N, 14, 2] (force for 14 players)
        """
        # 1. Apply actions to players (entities 1-14)
        self.vel[:, 1:, :] += actions * self.dt
        
        # 2. Integrate position
        self.pos += self.vel * self.dt
        
        # 3. Handle Ball-Player Collisions (Vectorized)
        # dist: [N, 14]
        diff = self.pos[:, 1:, :] - self.pos[:, 0, :].unsqueeze(1)
        dist = torch.norm(diff, dim=-1)
        collision_mask = dist < 1.0
        
        # Impulse transfer (simplified elastic)
        # If player hits ball, ball gets player velocity
        if collision_mask.any():
            env_ids, player_ids = torch.where(collision_mask)
            self.vel[env_ids, 0] = self.vel[env_ids, player_ids + 1] * 1.5
            
        # 4. Field boundaries (Bounce)
        # x-bounds
        mask_x = (self.pos[:, :, 0].abs() > self.field_width / 2)
        self.vel[:, :, 0][mask_x] *= -0.5
        self.pos[:, :, 0] = torch.clamp(self.pos[:, :, 0], -self.field_width/2, self.field_width/2)
        
        # y-bounds
        mask_y = (self.pos[:, :, 1].abs() > self.field_height / 2)
        self.vel[:, :, 1][mask_y] *= -0.5
        self.pos[:, :, 1] = torch.clamp(self.pos[:, :, 1], -self.field_height/2, self.field_height/2)

        # 5. Apply friction
        self.vel *= self.friction

    def get_state(self) -> Dict[str, torch.Tensor]:
        return {
            "ball_pos": self.pos[:, 0, :],
            "player_pos": self.pos[:, 1:, :],
            "ball_vel": self.vel[:, 0, :],
            "player_vel": self.vel[:, 1:, :]
        }
