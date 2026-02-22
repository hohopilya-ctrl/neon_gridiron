from __future__ import annotations

from typing import Any

import numpy as np

from sim.core.state import TeamID


class RewardShaper:
    """Hierarchical reward model for 7v7 tactical behaviors."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.cfg = config or {}
        self.w_goal = float(self.cfg.get("w_goal", 8.0))
        self.w_concede = float(self.cfg.get("w_concede", -6.0))
        self.w_progression = float(self.cfg.get("w_progression", 0.03))
        self.w_final_third = float(self.cfg.get("w_final_third", 0.35))
        self.w_possession = float(self.cfg.get("w_possession", 0.08))
        self.w_ball_dist = float(self.cfg.get("w_ball_dist", 0.14))
        self.w_compactness = float(self.cfg.get("w_compactness", 0.1))
        self.w_spectacle = float(self.cfg.get("w_spectacle", 0.04))

    def compute_meta_reward(self, state: Any, events: list[Any]) -> dict[str, float]:
        rewards = {
            "total": 0.0,
            "goal": 0.0,
            "offense": 0.0,
            "defense": 0.0,
            "dense": 0.0,
            "spec": 0.0,
        }

        for ev in events:
            ev_type = getattr(ev, "event_type", "")
            params = getattr(ev, "params", {}) or {}

            if ev_type == "GOAL":
                if params.get("team") == "BLUE":
                    rewards["goal"] += self.w_goal
                else:
                    rewards["goal"] += self.w_concede
            elif ev_type == "PROGRESSION":
                rewards["offense"] += self.w_progression * float(params.get("delta_x", 0.0))
            elif ev_type == "FINAL_THIRD_ENTRY":
                rewards["offense"] += self.w_final_third
            elif ev_type == "POSSESSION" and params.get("team") == "BLUE":
                rewards["dense"] += self.w_possession

        rewards["dense"] += self._ball_support_density(state)
        rewards["defense"] += self._defensive_compactness_bonus(state)
        rewards["spec"] += float(getattr(state, "spectacle_score", 0.0)) * self.w_spectacle

        rewards["total"] = (
            rewards["goal"]
            + rewards["offense"]
            + rewards["defense"]
            + rewards["dense"]
            + rewards["spec"]
        )

        return rewards

    def _ball_support_density(self, state: Any) -> float:
        if not getattr(state, "players", None):
            return 0.0

        ball_pos = np.asarray(state.ball.pos, dtype=np.float32)
        blue_players = [p for p in state.players if p.team is TeamID.BLUE]
        if not blue_players:
            return 0.0

        dists = np.asarray(
            [
                float(np.linalg.norm(np.asarray(player.pos, dtype=np.float32) - ball_pos))
                for player in blue_players
            ],
            dtype=np.float32,
        )
        nearest = float(np.min(dists))
        support = float(np.mean(np.clip(1.0 - dists / 220.0, 0.0, 1.0)))

        return self.w_ball_dist * (0.7 * support + 0.3 * (1.0 / (1.0 + nearest / 50.0)))

    def _defensive_compactness_bonus(self, state: Any) -> float:
        red_players = [p for p in getattr(state, "players", []) if p.team is TeamID.RED]
        if not red_players:
            return 0.0

        coords = np.stack([np.asarray(p.pos, dtype=np.float32) for p in red_players], axis=0)
        center = np.mean(coords, axis=0)
        spread = float(np.mean(np.linalg.norm(coords - center, axis=1)))
        compactness = float(np.clip(1.0 - spread / 240.0, 0.0, 1.0))

        return self.w_compactness * compactness
