import numpy as np
from typing import List, Dict, Any, Optional
from sim.core.state import MatchState, TeamID, PlayerRole

class TacticalAnalyst:
    """
    Professional Match Analyst for Neon Gridiron.
    Computes compactness, pressure efficiency, and detects degenerate behaviors.
    """
    def __init__(self):
        self.pass_matrix = {TeamID.BLUE: {}, TeamID.RED: {}}
        self.possession_buffer: List[float] = [] # Track X-progression to detect loops
        
    def analyze_tick(self, state: MatchState) -> Dict[str, Any]:
        metrics = {
            "compactness": self._calc_compactness(state),
            "pressure_index": self._calc_pressure(state),
            "threat_map": self._generate_threat_data(state)
        }
        
        # Anti-Degenerate check
        metrics["degenerate_score"] = self._detect_degenerate_possession(state)
        
        return metrics

    def _calc_compactness(self, state: MatchState) -> Dict[TeamID, float]:
        """Measure how close team players are to their centroid."""
        results = {}
        for team in [TeamID.BLUE, TeamID.RED]:
            team_players = [p.pos for p in state.players if p.team == team]
            if not team_players:
                results[team] = 0.0
                continue
            
            centroid = np.mean(team_players, axis=0)
            avg_dist = np.mean([np.linalg.norm(p_pos - centroid) for p_pos in team_players])
            # Lower avg_dist = higher compactness. Normalize 0-1 (1.0 = very compact)
            results[team] = float(np.clip(1.0 - (avg_dist / 150.0), 0.0, 1.0))
        return results

    def _calc_pressure(self, state: MatchState) -> float:
        """Measure intensity of pressure on the ball carrier."""
        if not state.possession_player_id:
            return 0.0
            
        poss_player = next((p for p in state.players if p.id == state.possession_player_id), None)
        if not poss_player: return 0.0
        
        opp_team = TeamID.RED if poss_player.team == TeamID.BLUE else TeamID.BLUE
        opponents = [p for p in state.players if p.team == opp_team]
        
        dists = [np.linalg.norm(p.pos - poss_player.pos) for p in opponents]
        nearby = [d for d in dists if d < 80.0]
        if not nearby: return 0.0
        
        return float(np.mean([1.0 - (d / 80.0) for d in nearby]))

    def _detect_degenerate_possession(self, state: MatchState) -> float:
        """ Detect 'Carousel' possession (passing without progression). """
        if state.possession_team is None: return 0.0
        
        self.possession_buffer.append(float(state.ball.pos[0]))
        if len(self.possession_buffer) > 300: # 5 seconds
            self.possession_buffer.pop(0)
            
        if len(self.possession_buffer) < 300: return 0.0
        
        # Check variance in X-progression
        x_std = np.std(self.possession_buffer)
        # If ball stays in the same X-zone too long, it's degenerate
        if x_std < 20.0:
            return 1.0
        return 0.0

    def _generate_threat_data(self, state: MatchState) -> List[Dict[str, Any]]:
        """Identify high-threat zones based on ball position and goal proximity."""
        # This will be expanded for UI overlays
        return []

    def record_pass(self, team: TeamID, from_id: str, to_id: str):
        key = (from_id, to_id)
        self.pass_matrix[team][key] = self.pass_matrix[team].get(key, 0) + 1
