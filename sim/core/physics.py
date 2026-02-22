from typing import Dict, Optional, Tuple

import numpy as np
import pymunk

from sim.core.rng import DeterministicRNG


class PhysicsEngine:
    """
    High-fidelity physics simulation for Neon Gridiron using Pymunk.
    Optimized for determinism with fixed DT and bit-identical updates.
    """

    def __init__(self, pitch_dim: Tuple[float, float], rng: DeterministicRNG):
        self.width, self.height = pitch_dim
        self.rng = rng
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.95  # Base damping for the entire world

        self.player_map: Dict[str, Tuple[pymunk.Body, pymunk.Circle]] = {}
        self.ball_elements: Optional[Tuple[pymunk.Body, pymunk.Circle]] = None

        self._init_field()

    def _init_field(self):
        """Create static boundaries of the futuristic neon arena."""
        static_body = self.space.static_body

        # Walls with moderate elasticity
        segments = [
            pymunk.Segment(static_body, (0, 0), (self.width, 0), 5),
            pymunk.Segment(static_body, (self.width, 0), (self.width, self.height), 5),
            pymunk.Segment(static_body, (self.width, self.height), (0, self.height), 5),
            pymunk.Segment(static_body, (0, self.height), (0, 0), 5),
        ]
        for seg in segments:
            seg.elasticity = 0.8
            seg.friction = 0.2
            seg.filter = pymunk.ShapeFilter(categories=0b01)
            self.space.add(seg)

    def spawn_player(self, player_id: str, pos: Tuple[float, float]) -> pymunk.Body:
        """Add a player bot to the physical world."""
        mass = 70.0
        radius = 12.0
        moment = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, moment)
        body.position = pos

        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.1
        shape.friction = 0.5
        shape.filter = pymunk.ShapeFilter(categories=0b10)

        self.space.add(body, shape)
        self.player_map[player_id] = (body, shape)
        return body

    def spawn_ball(self, pos: Tuple[float, float]) -> pymunk.Body:
        """Add the official Neon Ball to the arena."""
        mass = 0.45
        radius = 8.0
        moment = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, moment)
        body.position = pos

        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.9
        shape.friction = 0.1
        shape.filter = pymunk.ShapeFilter(categories=0b100)

        self.space.add(body, shape)
        self.ball_elements = (body, shape)
        return body

    def step(self, dt: float):
        """Advance simulation by a fixed time step."""
        # Custom logic for Magnus effect and drag can go here
        self.space.step(dt)

    def apply_action(self, player_id: str, force: Tuple[float, float], dash: bool = False):
        """Apply normalized bot actions into physics forces."""
        body, _ = self.player_map[player_id]
        multiplier = 2000.0 if not dash else 5000.0
        body.apply_force_at_local_point((force[0] * multiplier, force[1] * multiplier))

    def get_player_data(self, player_id: str) -> Tuple[np.ndarray, np.ndarray]:
        body, _ = self.player_map[player_id]
        return np.array(body.position), np.array(body.velocity)

    def get_ball_data(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.ball_elements is None:
            return np.zeros(2), np.zeros(2)
        body, _ = self.ball_elements
        return np.array(body.position), np.array(body.velocity)
