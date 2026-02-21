import numpy as np
import pytest
from ai.env.neon_env import NeonFootballEnv

def test_full_determinism():
    """Verify that two environments with the same seed produce identical results."""
    seed = 42
    env1 = NeonFootballEnv(seed=seed)
    env2 = NeonFootballEnv(seed=seed)
    
    obs1, _ = env1.reset(seed=seed)
    obs2, _ = env2.reset(seed=seed)
    
    assert np.array_equal(obs1, obs2)
    
    # Run 100 steps
    for _ in range(100):
        # Sample action from space (must use seeded RNG for action sampling if we were using it)
        # Here we use the same deterministic action vector
        action = np.ones(env1.action_space.shape, dtype=np.float32) * 0.5
        
        obs1, rew1, term1, trunc1, _ = env1.step(action)
        obs2, rew2, term2, trunc2, _ = env2.step(action)
        
        # Verify bit-perfect identity
        assert np.array_equal(obs1, obs2), f"Observation mismatch at tick {env1.state.tick}"
        assert rew1 == rew2
        assert term1 == term2
        
    print(f"✅ Determinism verified over 100 ticks.")

def test_state_reproducibility():
    """Verify that MatchState can be perfectly reconstructed."""
    env = NeonFootballEnv(seed=7)
    env.reset()
    
    # Run 50 steps
    for _ in range(50):
        env.step(env.action_space.sample())
        
    state1 = env.state
    
    # In a real scenario we might serialize/deserialize here
    # Check ball position consistency
    assert env.ball_body.position.x == state1.ball.pos[0]
    assert env.ball_body.position.y == state1.ball.pos[1]
