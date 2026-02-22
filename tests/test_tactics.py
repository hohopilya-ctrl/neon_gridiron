import numpy as np

from ai.env.neon_env import NeonFootballEnv
from ai.tactics.coach import TacticalCoach
from ai.tactics.formation import FormationPlanner
from sim.core.state import TeamID


def test_formation_targets_shape():
    planner = FormationPlanner()
    targets = planner.shifted_targets(
        TeamID.BLUE,
        ball_pos=np.array([320.0, 210.0], dtype=np.float32),
        possession_team=TeamID.BLUE,
    )
    assert targets.shape == (7, 2)


def test_tactical_coach_mode_is_valid():
    env = NeonFootballEnv({"seed": 12})
    env.reset()
    coach = TacticalCoach()

    decision = coach.choose_mode(env.state, team=TeamID.BLUE)
    assert decision.mode in {"build_up", "finalize", "recovery_block", "press"}
    assert 0.0 <= decision.confidence <= 1.0


def test_formation_error_is_deterministic():
    env1 = NeonFootballEnv({"seed": 99})
    env2 = NeonFootballEnv({"seed": 99})
    env1.reset()
    env2.reset()

    coach = TacticalCoach()
    e1 = coach.formation_error(env1.state, TeamID.BLUE)
    e2 = coach.formation_error(env2.state, TeamID.BLUE)
    assert np.isclose(e1, e2)
