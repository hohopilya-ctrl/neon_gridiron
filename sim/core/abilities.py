from dataclasses import dataclass
from typing import Dict


@dataclass
class Ability:
    id: str
    name: str
    energy_cost: float
    cooldown_ticks: int
    heat_per_use: float  # Anti-spam


class AbilityManager:
    """
    Advanced Ability Manager with energy and heat mechanics.
    """

    def __init__(self, registry: Dict[str, Ability]):
        self.registry = registry
        self.active_heat = {}  # actor_id -> heat_float

    def can_cast(self, actor_id: str, ability_id: str, current_energy: float) -> bool:
        ability = self.registry.get(ability_id)
        if not ability:
            return False
        if current_energy < ability.energy_cost:
            return False
        if self.active_heat.get(actor_id, 0) > 80.0:
            return False  # Overheated
        return True

    def cast(self, actor_id: str, ability_id: str):
        ability = self.registry[ability_id]
        self.active_heat[actor_id] = self.active_heat.get(actor_id, 0) + ability.heat_per_use
        return ability

    def update(self):
        """Decay heat over time."""
        for aid in list(self.active_heat.keys()):
            self.active_heat[aid] = max(0, self.active_heat[aid] * 0.99)
