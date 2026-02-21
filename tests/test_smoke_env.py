import gymnasium as gym
import numpy as np
import pytest
from ai.env.neon_env import NeonFootballEnv


def test_env_smoke():
    """Verify that the environment can be initialized and stepped."""
    env = NeonFootballEnv(seed=42)
    obs, info = env.reset()

    assert obs.shape == (88,)
    assert isinstance(obs, np.ndarray)

    # Take 5 steps with random actions
    for _ in range(5):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        assert obs.shape == (88,)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)

    env.close()


if __name__ == "__main__":
    test_env_smoke()
    print("✅ Smoke test passed!")
