import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from ai.training.elo import EloSystem

class LeagueManager:
    """
    Manages the population of agents and their rankings.
    Saves and loads league state for persistent training.
    """
    def __init__(self, save_path: str = "data/league.json"):
        self.save_path = save_path
        self.agents: Dict[str, Dict] = {} # id -> {rating, version, games}
        self.elo = EloSystem()
        self.load()

    def add_agent(self, agent_id: str, version: str = "v1"):
        if agent_id not in self.agents:
            self.agents[agent_id] = {
                "rating": 1000.0,
                "version": version,
                "games": 0,
                "last_update": datetime.now().isoformat()
            }

    def record_match(self, blue_id: str, red_id: str, blue_score: int, red_score: int):
        if blue_score > red_score:
            outcome = 1.0
        elif blue_score < red_score:
            outcome = 0.0
        else:
            outcome = 0.5
            
        r_blue = self.agents[blue_id]["rating"]
        r_red = self.agents[red_id]["rating"]
        
        new_blue, new_red = self.elo.update_ratings(r_blue, r_red, outcome)
        
        self.agents[blue_id]["rating"] = new_blue
        self.agents[blue_id]["games"] += 1
        self.agents[red_id]["rating"] = new_red
        self.agents[red_id]["games"] += 1
        
        self.save()

    def get_leaderboard(self) -> List[Tuple[str, float]]:
        sorted_agents = sorted(self.agents.items(), key=lambda x: x[1]["rating"], reverse=True)
        return [(k, v["rating"]) for k, v in sorted_agents]

    def save(self):
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, 'w') as f:
            json.dump(self.agents, f, indent=4)

    def load(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r') as f:
                self.agents = json.load(f)
