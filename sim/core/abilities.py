from dataclasses import dataclass
from typing import Dict, List, Optional

from sim.core.state import PlayerState


@dataclass(frozen=True)
class Ability:
    id: str
    name: str
    energy_cost: float
    stamina_penalty: float
    cooldown_ticks: int
    heat_per_use: float


class AbilityManager:
    """
    Manages casting, cooldowns, and resource pools for player bots.
    Implements futuristic energy-based skill system.
    """

    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, int]] = {}  # player_id -> {ability_id -> tick_ready}
        self.registry: Dict[str, Ability] = self._init_registry()

    def _init_registry(self) -> Dict[str, Ability]:
        return {
            "dash": Ability("dash", "Neon Dash", 10.0, 5.0, 120, 20.0),
            "blast": Ability("blast", "Sonic Blast", 40.0, 10.0, 300, 50.0),
            "teleport": Ability("teleport", "Phase Shift", 80.0, 20.0, 600, 80.0),
        }

    def can_cast(self, player: PlayerState, ability_id: str, tick: int) -> bool:
        ability = self.registry.get(ability_id)
        if not ability:
            return False

        # Resource checks
        if player.energy < ability.energy_cost:
            return False
        if player.heat > 90.0:
            return False  # Overheated state

        # Cooldown checks
        p_cd = self.cooldowns.get(player.id, {})
        if tick < p_cd.get(ability_id, 0):
            return False

        return True

    def cast(self, player: PlayerState, ability_id: str, tick: int) -> Optional[Ability]:
        if not self.can_cast(player, ability_id, tick):
            return None

        ability = self.registry[ability_id]
        player.energy -= ability.energy_cost
        player.stamina -= ability.stamina_penalty
        player.heat += ability.heat_per_use

        # Set cooldown
        self.cooldowns.setdefault(player.id, {})[ability_id] = tick + ability.cooldown_ticks
        return ability

    def update(self, players: List[PlayerState]):
        """Decay heat and regen energy over time."""
        for p in players:
            p.heat = max(0.0, p.heat * 0.99)
            p.energy = min(100.0, p.energy + 0.2)
