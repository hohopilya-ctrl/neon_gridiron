from typing import List, Dict
import numpy as np

class Referee:
    """
    Manages fouls, penalty points, and cards.
    """
    def __init__(self):
        self.penalty_points = {} # agent_id -> float
        self.cards = {} # agent_id -> list

    def check_foul(self, player_a, player_b):
        # Detect collision intensity or rule violation
        dist = player_a["body"].position.get_distance(player_b["body"].position)
        if dist < 8.0:
            rel_vel = (player_a["body"].velocity - player_b["body"].velocity).length
            if rel_vel > 15.0:
                self._assign_points(player_a["id"], rel_vel * 0.5)
                return True
        return False

    def _assign_points(self, agent_id, points):
        self.penalty_points[agent_id] = self.penalty_points.get(agent_id, 0) + points
        if self.penalty_points[agent_id] > 50.0:
            self.cards[agent_id] = self.cards.get(agent_id, []) + ["YELLOW"]
            self.penalty_points[agent_id] -= 50.0
# lines: 25
