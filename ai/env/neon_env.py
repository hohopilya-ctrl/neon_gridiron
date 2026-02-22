from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from ai.training.rewards import RewardShaper
from sim.core.rng import DeterministicRNG
from sim.core.rules import RulesEngine
from sim.core.state import BallState, MatchEvent, MatchState, PlayerState, TeamID


@dataclass(frozen=True)
class RoleSlot:
    name: str
    blue_pos: tuple[float, float]
    red_pos: tuple[float, float]


ROLE_SLOTS: tuple[RoleSlot, ...] = (
    RoleSlot("GK", (36.0, 200.0), (564.0, 200.0)),
    RoleSlot("LCB", (132.0, 110.0), (468.0, 110.0)),
    RoleSlot("RCB", (132.0, 290.0), (468.0, 290.0)),
    RoleSlot("LM", (264.0, 95.0), (336.0, 95.0)),
    RoleSlot("CM", (252.0, 200.0), (348.0, 200.0)),
    RoleSlot("RM", (264.0, 305.0), (336.0, 305.0)),
    RoleSlot("ST", (396.0, 200.0), (204.0, 200.0)),
)


class NeonFootballEnv(gym.Env[np.ndarray, np.ndarray]):
    """Deterministic 7v7 football environment with richer tactical signals."""

    metadata = {"render_modes": []}

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__()
        self.config = config or {}
        self.seed_value = int(self.config.get("seed", 42))
        self.rng = DeterministicRNG(self.seed_value)

        self.pitch_w = float(self.config.get("pitch_w", 600.0))
        self.pitch_h = float(self.config.get("pitch_h", 400.0))
        self.max_steps = int(self.config.get("max_steps", 600))

        self.max_player_speed = float(self.config.get("max_player_speed", 7.25))
        self.max_ball_speed = float(self.config.get("max_ball_speed", 14.0))
        self.player_accel = float(self.config.get("player_accel", 2.6))
        self.ball_friction = float(self.config.get("ball_friction", 0.962))
        self.player_friction = float(self.config.get("player_friction", 0.91))

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(28,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(64,),
            dtype=np.float32,
        )

        self.rules = RulesEngine((self.pitch_w, self.pitch_h))
        self.reward_shaper = RewardShaper()
        self.state = MatchState(players=[], ball=BallState())

        self._step_count = 0
        self._event_counter = 0
        self._last_ball_pos = np.zeros(2, dtype=np.float32)
        self._blue_target = np.array([self.pitch_w, self.pitch_h * 0.5], dtype=np.float32)
        self._red_target = np.array([0.0, self.pitch_h * 0.5], dtype=np.float32)

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
        self._event_counter = 0

        self.state.tick = 0
        self.state.score = {TeamID.BLUE: 0, TeamID.RED: 0}
        self.state.events = []
        self.state.spectacle_score = 0.0

        self.state.ball = BallState(
            pos=np.array([self.pitch_w * 0.5, self.pitch_h * 0.5], dtype=np.float32),
            vel=np.zeros(2, dtype=np.float32),
        )
        self._last_ball_pos = self.state.ball.pos.copy()
        self.state.players = self._spawn_teams()

        return self._build_observation(), {"seed": self.seed_value}

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        action = np.asarray(action, dtype=np.float32).reshape(self.action_space.shape)

        self.state.tick += 1
        self._step_count += 1
        self.state.events = []

        self._update_players(action)
        self._update_ball(action)

        goal_team = self.rules.check_goal(self.state.ball.pos)
        terminated = goal_team is not None
        if goal_team is TeamID.BLUE:
            self.state.score[TeamID.BLUE] += 1
            self._push_event("GOAL", params={"team": "BLUE"})
        elif goal_team is TeamID.RED:
            self.state.score[TeamID.RED] += 1
            self._push_event("GOAL", params={"team": "RED"})

        if self.state.ball.last_touch_team is TeamID.BLUE:
            self._push_event("POSSESSION", params={"team": "BLUE"})
        elif self.state.ball.last_touch_team is TeamID.RED:
            self._push_event("POSSESSION", params={"team": "RED"})

        reward_parts = self.reward_shaper.compute_meta_reward(self.state, self.state.events)
        reward = float(reward_parts["total"])

        truncated = self._step_count >= self.max_steps
        info = {
            "reward_parts": reward_parts,
            "score": {
                "blue": self.state.score[TeamID.BLUE],
                "red": self.state.score[TeamID.RED],
            },
        }

        return self._build_observation(), reward, bool(terminated), bool(truncated), info

    def _spawn_teams(self) -> list[PlayerState]:
        players: list[PlayerState] = []
        for idx, slot in enumerate(ROLE_SLOTS):
            jitter = np.array([self.rng.normal(0.0, 1.0), self.rng.normal(0.0, 1.0)], dtype=np.float32)
            players.append(
                PlayerState(
                    id=f"blue_{slot.name.lower()}_{idx}",
                    team=TeamID.BLUE,
                    pos=np.array(slot.blue_pos, dtype=np.float32) + jitter,
                    vel=np.zeros(2, dtype=np.float32),
                    stamina=100.0,
                    energy=100.0,
                    active_tags=[slot.name],
                )
            )

        for idx, slot in enumerate(ROLE_SLOTS):
            jitter = np.array([self.rng.normal(0.0, 1.0), self.rng.normal(0.0, 1.0)], dtype=np.float32)
            players.append(
                PlayerState(
                    id=f"red_{slot.name.lower()}_{idx}",
                    team=TeamID.RED,
                    pos=np.array(slot.red_pos, dtype=np.float32) + jitter,
                    vel=np.zeros(2, dtype=np.float32),
                    stamina=100.0,
                    energy=100.0,
                    active_tags=[slot.name],
                )
            )
        return players

    def _update_players(self, action: np.ndarray) -> None:
        for idx, player in enumerate(self.state.players):
            control = action[idx * 2 : idx * 2 + 2]
            control = np.clip(control, -1.0, 1.0)

            fatigue = np.clip(player.stamina / 100.0, 0.3, 1.0)
            accel = control * (self.player_accel * fatigue)
            player.vel = (player.vel + accel) * self.player_friction
            speed = float(np.linalg.norm(player.vel))
            if speed > self.max_player_speed:
                player.vel *= self.max_player_speed / speed

            player.pos = player.pos + player.vel
            player.pos[0] = np.clip(player.pos[0], 0.0, self.pitch_w)
            player.pos[1] = np.clip(player.pos[1], 0.0, self.pitch_h)

            workload = float(np.linalg.norm(control))
            player.stamina = float(np.clip(player.stamina - 0.05 - workload * 0.08, 45.0, 100.0))
            player.energy = player.stamina

    def _update_ball(self, action: np.ndarray) -> None:
        self._last_ball_pos = self.state.ball.pos.copy()

        closest_idx, min_dist = self._closest_player_to_ball()
        closest_player = self.state.players[closest_idx]

        touch_radius = 15.5
        if min_dist <= touch_radius:
            control = action[closest_idx * 2 : closest_idx * 2 + 2]
            kick_strength = float(np.linalg.norm(control))
            direction = np.asarray(control, dtype=np.float32)
            if kick_strength > 1e-6:
                direction = direction / (kick_strength + 1e-6)
                self.state.ball.vel = (
                    self.state.ball.vel * 0.65 + direction * (3.2 + 3.6 * kick_strength)
                )
                self.state.ball.last_touch_id = closest_player.id
                self.state.ball.last_touch_team = closest_player.team
                self._push_event("BALL_TOUCH", actor_id=closest_player.id)

        self.state.ball.vel = self.state.ball.vel * self.ball_friction
        speed = float(np.linalg.norm(self.state.ball.vel))
        if speed > self.max_ball_speed:
            self.state.ball.vel *= self.max_ball_speed / speed

        self.state.ball.pos = self.state.ball.pos + self.state.ball.vel
        self.state.ball.pos[0] = np.clip(self.state.ball.pos[0], 0.0, self.pitch_w)
        self.state.ball.pos[1] = np.clip(self.state.ball.pos[1], 0.0, self.pitch_h)

        if self.state.ball.last_touch_team is TeamID.BLUE:
            forward = float(self.state.ball.pos[0] - self._last_ball_pos[0])
            if forward > 0.7:
                self._push_event("PROGRESSION", params={"delta_x": forward})
            if self.state.ball.pos[0] > self.pitch_w * 0.75 and self._last_ball_pos[0] <= self.pitch_w * 0.75:
                self._push_event("FINAL_THIRD_ENTRY")
        elif self.state.ball.last_touch_team is TeamID.RED:
            forward = float(self._last_ball_pos[0] - self.state.ball.pos[0])
            if forward > 0.7:
                self._push_event("PROGRESSION", params={"delta_x": forward})
            if self.state.ball.pos[0] < self.pitch_w * 0.25 and self._last_ball_pos[0] >= self.pitch_w * 0.25:
                self._push_event("FINAL_THIRD_ENTRY")

    def _closest_player_to_ball(self) -> tuple[int, float]:
        dists = [float(np.linalg.norm(player.pos - self.state.ball.pos)) for player in self.state.players]
        idx = int(np.argmin(dists))
        return idx, dists[idx]

    def _push_event(
        self,
        event_type: str,
        actor_id: str | None = None,
        target_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> None:
        self._event_counter += 1
        self.state.events.append(
            MatchEvent(
                event_id=f"ev_{self.state.tick}_{self._event_counter}",
                tick=self.state.tick,
                event_type=event_type,
                actor_id=actor_id,
                target_id=target_id,
                params=params or {},
            )
        )

    def _build_observation(self) -> np.ndarray:
        obs = np.zeros(64, dtype=np.float32)

        # block 1: ball + score + phase
        obs[0:2] = self.state.ball.pos / np.array([self.pitch_w, self.pitch_h], dtype=np.float32)
        obs[2:4] = self.state.ball.vel / self.max_ball_speed
        obs[4] = self.state.score[TeamID.BLUE] / 10.0
        obs[5] = self.state.score[TeamID.RED] / 10.0
        obs[6] = min(self._step_count / float(self.max_steps), 1.0)

        # block 2: team tactical context
        blue_centroid, red_centroid = self._team_centroids()
        obs[8:10] = blue_centroid / np.array([self.pitch_w, self.pitch_h], dtype=np.float32)
        obs[10:12] = red_centroid / np.array([self.pitch_w, self.pitch_h], dtype=np.float32)
        obs[12] = self._team_compactness(TeamID.BLUE)
        obs[13] = self._team_compactness(TeamID.RED)

        # block 3: compact player slices (first 12 players x 4 features)
        cursor = 16
        for player in self.state.players[:12]:
            obs[cursor : cursor + 2] = player.pos / np.array([self.pitch_w, self.pitch_h], dtype=np.float32)
            obs[cursor + 2 : cursor + 4] = player.vel / self.max_player_speed
            cursor += 4
            if cursor >= 64:
                break

        return obs

    def _team_centroids(self) -> tuple[np.ndarray, np.ndarray]:
        blue = np.stack([p.pos for p in self.state.players if p.team is TeamID.BLUE], axis=0)
        red = np.stack([p.pos for p in self.state.players if p.team is TeamID.RED], axis=0)
        return np.mean(blue, axis=0), np.mean(red, axis=0)

    def _team_compactness(self, team: TeamID) -> float:
        coords = np.stack([p.pos for p in self.state.players if p.team is team], axis=0)
        center = np.mean(coords, axis=0)
        mean_dist = np.mean(np.linalg.norm(coords - center, axis=1))
        return float(np.clip(1.0 - mean_dist / 220.0, 0.0, 1.0))
