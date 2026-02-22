from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ai.tactics.formation import FormationPlanner
from sim.core.state import MatchState, TeamID


@dataclass(frozen=True)
class TacticalDecision:
    mode: str
    target_player_id: str | None
    confidence: float
    reason: str


class TacticalCoach:
    """Rule-guided tactical advisor for bootstrapping multi-agent behavior."""

    def __init__(self):
        self.formation = FormationPlanner()

    def choose_mode(self, state: MatchState, team: TeamID = TeamID.BLUE) -> TacticalDecision:
        ball = state.ball.pos
        possession = state.ball.last_touch_team

        if possession is team and self._is_in_final_third(ball, team):
            return TacticalDecision(
                mode="finalize",
                target_player_id=self._nearest_attacker(state, team),
                confidence=0.82,
                reason="possession in final third",
            )
        if possession is team:
            return TacticalDecision(
                mode="build_up",
                target_player_id=self._best_progression_option(state, team),
                confidence=0.74,
                reason="controlled possession in middle zones",
            )
        if self._dangerous_counter_risk(state, team):
            return TacticalDecision(
                mode="recovery_block",
                target_player_id=None,
                confidence=0.78,
                reason="defensive transition risk",
            )
        return TacticalDecision(
            mode="press",
            target_player_id=self._nearest_player_to_ball(state, team),
            confidence=0.69,
            reason="no possession, ball recoverable",
        )

    def formation_error(self, state: MatchState, team: TeamID = TeamID.BLUE) -> float:
        players = [p for p in state.players if p.team is team]
        if not players:
            return 0.0
        positions = np.stack([p.pos for p in players], axis=0)
        targets = self.formation.shifted_targets(team, state.ball.pos, state.ball.last_touch_team)
        if targets.shape[0] != positions.shape[0]:
            targets = targets[: positions.shape[0]]
        return float(np.mean(np.linalg.norm(positions - targets, axis=1)))

    def _is_in_final_third(self, ball_pos: np.ndarray, team: TeamID) -> bool:
        if team is TeamID.BLUE:
            return bool(ball_pos[0] >= 400.0)
        return bool(ball_pos[0] <= 200.0)

    def _dangerous_counter_risk(self, state: MatchState, team: TeamID) -> bool:
        if state.ball.last_touch_team is None or state.ball.last_touch_team is team:
            return False
        own_players = [p for p in state.players if p.team is team]
        if not own_players:
            return False
        own_center_x = float(np.mean([p.pos[0] for p in own_players]))
        ball_x = float(state.ball.pos[0])
        if team is TeamID.BLUE:
            return ball_x < own_center_x - 18.0
        return ball_x > own_center_x + 18.0

    def _nearest_player_to_ball(self, state: MatchState, team: TeamID) -> str | None:
        players = [p for p in state.players if p.team is team]
        if not players:
            return None
        idx = int(np.argmin([np.linalg.norm(p.pos - state.ball.pos) for p in players]))
        return players[idx].id

    def _nearest_attacker(self, state: MatchState, team: TeamID) -> str | None:
        players = [p for p in state.players if p.team is team]
        if not players:
            return None
        if team is TeamID.BLUE:
            idx = int(np.argmax([p.pos[0] for p in players]))
        else:
            idx = int(np.argmin([p.pos[0] for p in players]))
        return players[idx].id

    def _best_progression_option(self, state: MatchState, team: TeamID) -> str | None:
        players = [p for p in state.players if p.team is team]
        if not players:
            return None

        if team is TeamID.BLUE:
            weights = [0.65 * p.pos[0] - 0.35 * abs(p.pos[1] - 200.0) for p in players]
        else:
            weights = [0.65 * (600.0 - p.pos[0]) - 0.35 * abs(p.pos[1] - 200.0) for p in players]

        idx = int(np.argmax(weights))
        return players[idx].id
