import numpy as np
import pytest
from ai.env.neon_env import NeonFootballEnv

def test_strict_determinism():
    """Verify that two environments with the same seed produce exactly the same states."""
    seed = 12345
    env1 = NeonFootballEnv(seed=seed)
    env2 = NeonFootballEnv(seed=seed)
    
    obs1, _ = env1.reset()
    obs2, _ = env2.reset()
    
    assert np.array_equal(obs1, obs2), "Initial observations must be identical"
    
    # Take 100 steps with identical actions
    for step in range(100):
        # Sample action once and use for both
        action = env1.action_space.sample()
        
        obs1, rew1, term1, trunc1, _ = env1.step(action)
        obs2, rew2, term2, trunc2, _ = env2.step(action)
        
        assert np.array_equal(obs1, obs2), f"Observations diverged at step {step}"
        assert rew1 == rew2, f"Rewards diverged at step {step}"
        assert term1 == term2, f"Termination diverged at step {step}"
        
def test_seed_reset():
    """Verify that resetting with the same seed reproduces the same trajectory."""
    env = NeonFootballEnv(seed=777)
    
    # Run 1
    env.reset(seed=777)
    actions = [env.action_space.sample() for _ in range(50)]
    states1 = []
    for a in actions:
        obs, _, _, _, _ = env.step(a)
        states1.append(obs)
        
    # Run 2
    env.reset(seed=777)
    states2 = []
    for a in actions:
        obs, _, _, _, _ = env.step(a)
        states2.append(obs)
        
    for i in range(len(states1)):
        assert np.array_equal(states1[i], states2[i]), f"Divergence at step {i} after reset"

if __name__ == "__main__":
    pytest.main([__file__])
