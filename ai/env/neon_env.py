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

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(56,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(64,),
            dtype=np.float32,
        )

        from sim.core.physics import PhysicsEngine
        self.physics = PhysicsEngine((600.0, 400.0), self.rng)
        self.rules = RulesEngine((600.0, 400.0))
        
        from ai.training.reward_engine import RewardEngine
        self.reward_engine = RewardEngine()
        
        from ai.explainability.tactical_analyst import TacticalAnalyst
        self.analyst = TacticalAnalyst()
        
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

        # Reset Physics
        self.physics = None
        from sim.core.physics import PhysicsEngine
        self.physics = PhysicsEngine((600.0, 400.0), self.rng)

        self.state.tick = 0
        self.state.score = {TeamID.BLUE: 0, TeamID.RED: 0}
        self.state.events = []
        
        # Spawn Ball
        self.state.ball = BallState(
            pos=np.array([300.0, 200.0], dtype=np.float32),
            vel=np.zeros(2, dtype=np.float32),
        )
        self.physics.spawn_ball((300.0, 200.0))

        # Spawn Players with Roles
        self.state.players = []
        from sim.core.state import PlayerRole
        roles = [PlayerRole.GK, PlayerRole.DEF, PlayerRole.DEF, PlayerRole.MID, PlayerRole.MID, PlayerRole.FWD, PlayerRole.FWD]
        
        for idx in range(7):
            pid = f"blue_{idx}"
            pos = (120.0 + idx * 20.0, 60.0 + idx * 40.0)
            self.state.players.append(
                PlayerState(id=pid, team=TeamID.BLUE, role=roles[idx], pos=np.array(pos))
            )
            self.physics.spawn_player(pid, pos)

        for idx in range(7):
            pid = f"red_{idx}"
            pos = (480.0 - idx * 20.0, 60.0 + idx * 40.0)
            self.state.players.append(
                PlayerState(id=pid, team=TeamID.RED, role=roles[idx], pos=np.array(pos))
            )
            self.physics.spawn_player(pid, pos)

        return self._build_observation(), {"seed": self.seed_value}

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        action = np.asarray(action, dtype=np.float32).reshape(self.action_space.shape)
        
        self.state.tick += 1
        self._step_count += 1
        
        # 1. Physics Engine integration
        # Action is (28,) -> 7 players * [dx, dy, kick, dash]
        # For simplicity in this env, we control all players
        for i, player in enumerate(self.state.players):
            base = i * 4
            p_action = action[base:base+4]
            force = (p_action[0], p_action[1])
            kick = p_action[2] > 0.5
            dash = p_action[3] > 0.5
            
            # Stamina drain
            drain = 0.01 + (float(np.linalg.norm(force)) * 0.05)
            if dash: drain += 0.5
            player.stamina = max(0.0, player.stamina - drain)
            
            # Apply force if stamina remains
            if player.stamina > 1.0:
                self.physics.apply_action(player.id, force, dash=dash)
                if kick:
                    if self.rules.check_interaction(player.pos, self.state.ball.pos):
                        self.physics.apply_ball_impulse(force)
                        event_type = "SHOT" if np.linalg.norm(force) > 0.8 else "PASS"
                        self.state.events.append(MatchEvent(
                            event_id=f"tick_{self.state.tick}_{player.id}",
                            tick=self.state.tick,
                            event_type=event_type,
                            actor_id=player.id
                        ))
                        # Note: Simple pass detection (who touched before?)
                        # In full sim, this would use possession_player_id
                        if event_type == "PASS":
                             self.analyst.record_pass(player.team, player.id, "unnamed_target")
        
        self.physics.step(1.0/60.0)
        
        # Sync state from physics
        for player in self.state.players:
            p, v = self.physics.get_player_data(player.id)
            player.pos = p
            player.vel = v
            
        bp, bv = self.physics.get_ball_data()
        self.state.ball.pos = bp
        self.state.ball.vel = bv

        # 2. Tactical Analysis
        tactical_data = self.analyst.analyze_tick(self.state)
        self.state.pressure_index = tactical_data['pressure_index']
        
        # 3. Reward calculation
        reward = self.reward_engine.calculate(self.state, self.state.events, TeamID.BLUE)
        
        # Apply degenerate penalty
        if tactical_data['degenerate_score'] > 0.8:
            reward -= 0.1 # Penalty for carousel possession

        goal_team = self.rules.check_goal(self.state.ball.pos)
        terminated = goal_team is not None
        if goal_team is TeamID.BLUE:
            self.state.score[TeamID.BLUE] += 1
            reward += self.reward_engine.cfg['sparse']['goal_scored']
        elif goal_team is TeamID.RED:
            self.state.score[TeamID.RED] += 1
            reward += self.reward_engine.cfg['sparse']['goal_conceded']

        truncated = self._step_count >= self.max_steps

        # Clear events for next tick to avoid double counting
        self.state.events = []

        return self._build_observation(), reward, bool(terminated), bool(truncated), {}

    def _calculate_basic_reward(self) -> float:
        # Distance to goal reward
        dist_to_goal = np.linalg.norm(self.state.ball.pos - np.array([600.0, 200.0]))
        return -dist_to_goal / 600.0

        return obs

    def _build_observation(self) -> np.ndarray:
        obs = np.zeros(64, dtype=np.float32)
        # 1. Ball (4)
        obs[0:2] = self.state.ball.pos / 600.0
        obs[2:4] = self.state.ball.vel / 20.0
        
        # 2. Players (Reduced set to fit 60 remaining slots)
        # Each player: pos(2), team_code(1), role_encoded(1) = 4 values
        # We can fit 15 players (all 14)
        cursor = 4
        for i, player in enumerate(self.state.players):
            if i >= 14: break
            obs[cursor:cursor+2] = player.pos / 600.0
            obs[cursor+2] = 0.1 if player.team == TeamID.BLUE else 0.9
            # Role encoding: GK=0.1, DEF=0.3, MID=0.5, FWD=0.7
            role_map = {"GK": 0.1, "DEF": 0.3, "MID": 0.5, "FWD": 0.7}
            obs[cursor+3] = role_map.get(player.role.name[:3], 0.5)
            cursor += 4
            
        return obs

    def get_telemetry_frame(self) -> dict:
        """Returns a v2.2.0 compatible telemetry frame."""
        analyst_data = self.analyst.analyze_tick(self.state)
        
        frame = {
            "v": "2.2.0",
            "t": self.state.tick,
            "s": [self.state.score[TeamID.BLUE], self.state.score[TeamID.RED]],
            "b": {
                "p": [float(self.state.ball.pos[0]), float(self.state.ball.pos[1])],
                "v": [float(self.state.ball.vel[0]), float(self.state.ball.vel[1])]
            },
            "p": [],
            "pressure": float(analyst_data['pressure_index']),
            "compactness": {k.name: float(v) for k, v in analyst_data['compactness'].items()},
            "o": {
                "attn": [] # Attention map to be filled if available
            }
        }
        
        for p in self.state.players:
            frame["p"].append({
                "id": p.id,
                "team": 0 if p.team == TeamID.BLUE else 1,
                "pos": [float(p.pos[0]), float(p.pos[1])],
                "vel": [float(p.vel[0]), float(p.vel[1])],
                "st": float(p.stamina),
                "en": float(p.energy)
            })
            
        return frame
