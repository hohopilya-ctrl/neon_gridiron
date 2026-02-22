from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from sim.core.rng import DeterministicRNG
from sim.core.rules import RulesEngine
from sim.core.state import BallState, MatchState, PlayerState, TeamID


class NeonFootballEnv(gym.Env[np.ndarray, np.ndarray]):
    """Minimal deterministic 7v7 environment used by tests and training stubs."""

    metadata = {"render_modes": []}

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__()
        self.config = config or {}
        self.seed_value = int(self.config.get("seed", 42))
        self.rng = DeterministicRNG(self.seed_value)

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(28,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(64,),
            dtype=np.float32,
        )

        self.rules = RulesEngine((600.0, 400.0))
        self.state = MatchState(players=[], ball=BallState())
        self.max_steps = 600
        self._step_count = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del options
        if seed is not None:
            self.seed_value = int(seed)
        self.rng.reset(self.seed_value)
        self._step_count = 0

        self.state.tick = 0
        self.state.score = {TeamID.BLUE: 0, TeamID.RED: 0}
        self.state.events = []
        self.state.ball = BallState(
            pos=np.array([300.0, 200.0], dtype=np.float32),
            vel=np.zeros(2, dtype=np.float32),
        )

        self.state.players = []
        for idx in range(7):
            self.state.players.append(
                PlayerState(
                    id=f"blue_{idx}",
                    team=TeamID.BLUE,
                    pos=np.array([120.0 + idx * 20.0, 60.0 + idx * 40.0], dtype=np.float32),
                    vel=np.zeros(2, dtype=np.float32),
                )
            )
        for idx in range(7):
            self.state.players.append(
                PlayerState(
                    id=f"red_{idx}",
                    team=TeamID.RED,
                    pos=np.array([480.0 - idx * 20.0, 60.0 + idx * 40.0], dtype=np.float32),
                    vel=np.zeros(2, dtype=np.float32),
                )
            )

        return self._build_observation(), {"seed": self.seed_value}

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        action = np.asarray(action, dtype=np.float32).reshape(self.action_space.shape)

        self.state.tick += 1
        self._step_count += 1

        # Apply deterministic motion from action chunks [dx, dy, kick, dash]
        for idx, player in enumerate(self.state.players):
            base = idx * 2
            force = action[base : base + 2]
            player.vel = np.clip(force * 6.0, -6.0, 6.0)
            player.pos = player.pos + player.vel
            player.pos[0] = np.clip(player.pos[0], 0.0, 600.0)
            player.pos[1] = np.clip(player.pos[1], 0.0, 400.0)

        # Ball drifts deterministically toward average player impulse
        impulse = float(np.mean(action))
        self.state.ball.vel = np.array([impulse * 1.5, -impulse * 1.5], dtype=np.float32)
        self.state.ball.pos = np.clip(
            self.state.ball.pos + self.state.ball.vel,
            np.array([0.0, 0.0], dtype=np.float32),
            np.array([600.0, 400.0], dtype=np.float32),
        )

        reward = float(-np.linalg.norm(self.state.ball.pos - np.array([300.0, 200.0], dtype=np.float32)) / 1000.0)

        goal_team = self.rules.check_goal(self.state.ball.pos)
        terminated = goal_team is not None
        if goal_team is TeamID.BLUE:
            self.state.score[TeamID.BLUE] += 1
            reward += 1.0
        elif goal_team is TeamID.RED:
            self.state.score[TeamID.RED] += 1
            reward -= 1.0

        truncated = self._step_count >= self.max_steps

        return self._build_observation(), reward, bool(terminated), bool(truncated), {}

    def _build_observation(self) -> np.ndarray:
        obs = np.zeros(64, dtype=np.float32)
        obs[0:2] = self.state.ball.pos / np.array([600.0, 400.0], dtype=np.float32)
        obs[2:4] = self.state.ball.vel / 10.0

        cursor = 4
        for player in self.state.players[:14]:
            obs[cursor : cursor + 2] = player.pos / np.array([600.0, 400.0], dtype=np.float32)
            cursor += 2
            if cursor >= 64:
                break
        return obs
