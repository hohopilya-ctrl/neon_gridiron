import yaml
import numpy as np
from typing import Dict, Any, List
from sim.core.state import MatchState, TeamID, PlayerRole

class RewardEngine:
    """
    Multi-layered reward calculator for Neon Gridiron.
    Balances sparse goal-based rewards with dense tactical shaping.
    """
    def __init__(self, config_path: str = "configs/rewards.yaml", profile: str = "baseline"):
        with open(config_path, 'r') as f:
            full_cfg = yaml.safe_load(f)
            self.cfg = full_cfg.get(profile, full_cfg['baseline'])
            
    def calculate(self, state: MatchState, events: List[Any], team: TeamID) -> float:
        total_reward = 0.0
        
        # 1. Sparse Rewards (Goals)
        total_reward += self._sparse_reward(state, team)
        
        # 2. Dense Offense
        total_reward += self._offense_reward(state, events, team)
        
        # 3. Dense Defense
        total_reward += self._defense_reward(state, events, team)
        
        # 4. Discipline & Stamina
        total_reward += self._discipline_reward(state, team)
        
        return float(total_reward)

    def _sparse_reward(self, state: MatchState, team: TeamID) -> float:
        # Check goals in this tick (this logic depends on env handling)
        # For simplicity, we assume the caller handles the delta
        return 0.0 

    def _offense_reward(self, state: MatchState, events: List[Any], team: TeamID) -> float:
        reward = 0.0
        w = self.cfg['dense_offense']
        ball_pos = state.ball.pos
        
        # Ball Progression (Targeting X=600 for BLUE, X=0 for RED)
        if team == TeamID.BLUE:
            prog = ball_pos[0] / 600.0
            if ball_pos[0] > 400: reward += w['final_third_entry']
        else:
            prog = (600.0 - ball_pos[0]) / 600.0
            if ball_pos[0] < 200: reward += w['final_third_entry']
            
        reward += prog * w['progression']
        
        # Event Based
        for e in events:
            if getattr(e, 'actor_team', None) == team:
                if e.event_type == "PASS": reward += w['pass_complete']
                if e.event_type == "SHOT": reward += w['shot_taken']
                
        return reward

    def _defense_reward(self, state: MatchState, events: List[Any], team: TeamID) -> float:
        reward = 0.0
        w = self.cfg['dense_defense']
        
        # Pressure (Are we near the ball when opponent has it?)
        opp_team = TeamID.RED if team == TeamID.BLUE else TeamID.BLUE
        if state.possession_team == opp_team:
            for p in state.players:
                if p.team == team:
                    dist = np.linalg.norm(p.pos - state.ball.pos)
                    if dist < 100.0:
                        reward += (1.0 - dist/100.0) * w['pressure']
                        
        return reward

    def _discipline_reward(self, state: MatchState, team: TeamID) -> float:
        reward = 0.0
        w = self.cfg['discipline']
        
        for p in state.players:
            if p.team == team:
                if p.stamina < 20.0:
                    reward += w['stamina_penalty'] * (20.0 - p.stamina)
                    
        return reward
