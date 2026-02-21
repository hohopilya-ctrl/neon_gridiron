import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field

class PhysicsConfig(BaseModel):
    damping: float = Field(default=0.95, ge=0.8, le=1.0)
    gravity: float = 0.0

class MatchConfig(BaseModel):
    max_ticks: int = Field(default=2000, gt=0)
    team_size: int = Field(default=7, gt=0)
    field_size: tuple = (600, 400)

class GlobalConfig(BaseModel):
    physics: PhysicsConfig = Field(default_factory=PhysicsConfig)
    match: MatchConfig = Field(default_factory=MatchConfig)

def load_config(path: str = "configs/match_rules.yaml") -> GlobalConfig:
    """Loads and validates configuration from YAML."""
    config_path = Path(path)
    if not config_path.exists():
        return GlobalConfig()
        
    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}
        
    return GlobalConfig(**data)
