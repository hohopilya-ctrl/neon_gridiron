import pymunk
import numpy as np
from typing import Optional

class Engine2D:
    """
    Core physics engine using Pymunk.
    Handles player movement, ball physics, and Magnus effect.
    """
    def __init__(self, config: dict, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng()
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.damping = config.get('damping', 0.95)
        self.space.damping = self.damping
        self._init_field()

    def _init_field(self):
        # Field boundaries
        static_body = self.space.static_body
        lines = [
            pymunk.Segment(static_body, (0, 0), (600, 0), 2),
            pymunk.Segment(static_body, (600, 0), (600, 400), 2),
            pymunk.Segment(static_body, (600, 400), (0, 400), 2),
            pymunk.Segment(static_body, (0, 400), (0, 0), 2)
        ]
        for line in lines:
            line.elasticity = 0.8
            line.friction = 0.5
            self.space.add(line)

    def add_player(self, pos, team_id):
        body = pymunk.Body(70, float("inf"))
        body.position = pos
        shape = pymunk.Circle(body, 5)
        shape.elasticity = 0.2
        shape.friction = 0.5
        self.space.add(body, shape)
        return body

    def add_ball(self, pos):
        body = pymunk.Body(0.5, 0.5)
        body.position = pos
        shape = pymunk.Circle(body, 3)
        shape.elasticity = 0.9
        shape.friction = 0.1
        self.space.add(body, shape)
        return body

    def step(self, dt: float = 1.0/60.0):
        self.space.step(dt)

    def apply_magnus(self, ball_body, spin: float):
        # f = k * (v x s)
        vel = ball_body.velocity
        if vel.length > 0.1:
            force = pymunk.Vec2d(-vel.y, vel.x).normalized() * spin * 5.0
            ball_body.apply_force_at_local_point(force)
# lines: 50
