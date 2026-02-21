import pytest
import numpy as np
from sim.core.physics import Engine2D
from ai.env.neon_env import NeonFootballEnv


def test_physics_engine_init():
    """Verify that the physics engine initializes without crashing."""
    engine = Engine2D({})
    assert engine is not None


def test_env_step():
    """Verify standard step logic in Gymnasium environment."""
    env = NeonFootballEnv({})
    obs, info = env.reset()
    assert obs.shape == (88,)

    # Send zero actions
    action = np.zeros(env.action_space.shape, dtype=np.float32)
    obs, reward, term, trunc, info = env.step(action)

    assert not np.isnan(reward)
    assert obs.shape == (88,)


def test_team_assignment():
    """Verify that players are assigned to correct teams."""
    env = NeonFootballEnv()
    env.reset()
    blue_team = [p for p in env.state.players if p.team == 0]
    red_team = [p for p in env.state.players if p.team == 1]
    assert len(blue_team) == 7
    assert len(red_team) == 7
