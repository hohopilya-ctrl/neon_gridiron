import time

class Ability:
    def __init__(self, name: str, cost: float, cooldown: float):
        self.name = name
        self.cost = cost
        self.cooldown = cooldown
        self.last_used = 0

    def can_use(self, stamina: float) -> bool:
        return stamina >= self.cost and (time.time() - self.last_used) > self.cooldown

class AbilityManager:
    def __init__(self):
        self.abilities = {
            "DASH": Ability("DASH", 20.0, 1.5),
            "POWER_SHOT": Ability("POWER_SHOT", 35.0, 5.0),
            "TELEPORT": Ability("TELEPORT", 80.0, 15.0)
        }
        self.heat = 0.0 # Anti-spam global heat

    def cast(self, agent, ability_name):
        a = self.abilities.get(ability_name)
        if a and a.can_use(agent["stamina"]):
            a.last_used = time.time()
            agent["stamina"] -= a.cost
            self.heat += 5.0
            return True
        return False
# lines: 30
