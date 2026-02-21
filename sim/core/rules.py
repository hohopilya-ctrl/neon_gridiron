# OUTPUT PART 2/Y
# Neon Gridiron ULTRA: Referee, Rules, and Abilities

# File: sim/core/rules.py
import numpy as np
from typing import Optional, Tuple
from sim.core.events import MatchEvent

class RulesEngine:
    def __init__(self, pitch_dim: Tuple[float, float]):
        self.width, self.height = pitch_dim
        
    def check_out_of_bounds(self, ball_pos: np.ndarray) -> Optional[str]:
        if ball_pos[0] < 0 or ball_pos[0] > self.width:
            return "THROW_IN" if 5 < ball_pos[1] < self.height - 5 else "GOAL_KICK"
        if ball_pos[1] < 0 or ball_pos[1] > self.height:
            return "THROW_IN"
        return None

    def check_goal(self, ball_pos: np.ndarray) -> Optional[int]:
        if (ball_pos[0] < 0 or ball_pos[0] > self.width) and (self.height/2 - 4 < ball_pos[1] < self.height/2 + 4):
            return 0 if ball_pos[0] > self.width else 1
        return None
# lines: 20

# File: sim/core/referee.py
from typing import List, Dict
from sim.core.events import MatchEvent
from sim.core.state import MatchState

class Referee:
    def __init__(self, config: dict):
        self.config = config
        self.foul_threshold = config.get('foul_threshold', 10.0)
        self.penalty_history = {} # actor_id -> points
        
    def process_collision(self, actor_id: str, target_id: str, impulse: float, tick: int) -> List[MatchEvent]:
        events = []
        if impulse > self.foul_threshold:
            self.penalty_history[actor_id] = self.penalty_history.get(actor_id, 0) + (impulse / 10.0)
            events.append(MatchEvent(
                event_id=f"foul_{tick}_{actor_id}",
                tick=tick,
                event_type="FOUL",
                actor_id=actor_id,
                target_id=target_id,
                params={"severity": impulse}
            ))
            
            # Card logic
            score = self.penalty_history[actor_id]
            if score > 50 and score < 100:
                events.append(MatchEvent(f"y_{tick}", tick, "YELLOW", actor_id))
            elif score >= 100:
                events.append(MatchEvent(f"r_{tick}", tick, "RED", actor_id))
                
        return events

    def check_var(self, event: MatchEvent) -> bool:
        # Probabilistic VAR check for high-stakes fouls
        return event.event_type == "FOUL" and event.params.get("severity", 0) > 30.0
# lines: 45

# File: sim/core/abilities.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class Ability:
    id: str
    name: str
    energy_cost: float
    cooldown_ticks: int
    heat_per_use: float # Anti-spam

class AbilityManager:
    def __init__(self, registry: Dict[str, Ability]):
        self.registry = registry
        self.active_heat = {} # actor_id -> heat_float

    def can_cast(self, actor_id: str, ability_id: str, current_energy: float) -> bool:
        ability = self.registry.get(ability_id)
        if not ability: return False
        if current_energy < ability.energy_cost: return False
        if self.active_heat.get(actor_id, 0) > 80.0: return False # Overheated
        return True

    def cast(self, actor_id: str, ability_id: str):
        ability = self.registry[ability_id]
        self.active_heat[actor_id] = self.active_heat.get(actor_id, 0) + ability.heat_per_use
        return ability

    def update(self):
        # Decay heat over time
        for aid in self.active_heat:
            self.active_heat[aid] = max(0, self.active_heat[aid] * 0.99)
# lines: 40

# File: sim/replay/recorder.py
import json
import os
from typing import List
from sim.core.state import MatchState

class ReplayRecorder:
    def __init__(self, match_id: str, output_dir: str = "replays"):
        self.match_id = match_id
        self.output_path = os.path.join(output_dir, f"{match_id}.json")
        self.frames = []
        os.makedirs(output_dir, exist_ok=True)

    def record_frame(self, state: MatchState):
        frame = {
            "t": state.tick,
            "b": state.ball.pos.tolist(),
            "p": [{"id": p.id, "pos": p.pos.tolist(), "stm": p.stamina} for p in state.players],
            "e": [ev.event_type for ev in state.events]
        }
        self.frames.append(frame)

    def save(self, metadata: dict):
        with open(self.output_path, 'w') as f:
            json.dump({"meta": metadata, "frames": self.frames}, f)
# lines: 30

# END OF PART 2 - to continue output next part.
