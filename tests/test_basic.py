import pytest
import numpy as np
from sim.core.physics import PhysicsEngine
from sim.core.rng import DeterministicRNG

def test_physics_engine_init():
    """Verify that the physics engine initializes without crashing."""
    rng = DeterministicRNG(seed=42)
    engine = PhysicsEngine(pitch_dim=(600.0, 400.0), rng=rng)
    assert engine is not None


from ai.env.neon_env import NeonFootballEnv
from sim.core.state import TeamID

def test_env_step():
    """Verify standard step logic in Gymnasium environment."""
    env = NeonFootballEnv({"seed": 1})
    obs, info = env.reset()
    assert obs.shape == (64,)

    # Send zero actions
    action = np.zeros(env.action_space.shape, dtype=np.float32)
    obs, reward, term, trunc, info = env.step(action)

    assert not np.isnan(reward)
    assert obs.shape == (64,)

def test_team_assignment():
    """Verify that players are assigned to correct teams."""
    env = NeonFootballEnv()
    env.reset()
    blue_team = [p for p in env.state.players if p.team == TeamID.BLUE]
    red_team = [p for p in env.state.players if p.team == TeamID.RED]
    assert len(blue_team) == 7
    assert len(red_team) == 7
