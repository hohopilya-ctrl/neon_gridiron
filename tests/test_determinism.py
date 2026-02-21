import numpy as np

from ai.env.neon_env import NeonFootballEnv


def test_strict_determinism():
    """Verify that the simulation produces bit-identical results given the same seed."""
    env1 = NeonFootballEnv({"seed": 42})
    env2 = NeonFootballEnv({"seed": 42})

    obs1, _ = env1.reset()
    obs2, _ = env2.reset()

    assert np.array_equal(obs1, obs2)

    # Run 100 steps
    for _ in range(100):
        # Sample same action
        action = env1.action_space.sample()
        obs1, r1, t1, tr1, _ = env1.step(action)
        obs2, r2, t2, tr2, _ = env2.step(action)

        # Verify bit-identical state
        assert np.array_equal(obs1, obs2), "Observation divergence detected!"
        assert r1 == r2, "Reward divergence detected!"
        assert t1 == t2
        assert tr1 == tr2

    print("✅ Determinism test passed: Bit-identical results confirmed.")


def test_goal_logic():
    """Verify that scoring updates the match state correctly."""
    env = NeonFootballEnv({"seed": 1})
    env.reset()

    # Force ball into blue goal
    from sim.core.state import TeamID

    env.state.ball.pos = np.array([0.0, 200.0])  # Middle of goal
    goal = env.rules.check_goal(env.state.ball.pos)
    assert goal == TeamID.RED  # Blue conceded
