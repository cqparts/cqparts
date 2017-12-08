import cadquery

from .base import Thread
from ...params import *


class BallScrewThread(Thread):
    ball_radius = Float(0.25, doc="ball's radius")

    def build_profile(self):
        profile = cadquery.Workplane("XZ") \
            .moveTo(self.radius, self.pitch - self.ball_radius)
        # cylindrical face
        if (2 * self.ball_radius) < self.pitch:
            profile = profile.lineTo(self.radius, self.ball_radius)
        # rail for balls
        profile = profile.threePointArc(
                (self.radius - self.ball_radius, 0),
                (self.radius, -self.ball_radius)
            )
        return profile.wire()
