import cadquery

from .base import Thread
from ...params import *


class TriangularThread(Thread):
    radius_core = Float(2.5, doc="radius of valley")

    def build_profile(self):
        points = [
            (self.radius_core, 0),
            (self.radius, self.pitch/2),
            (self.radius_core, self.pitch),
        ]
        profile = cadquery.Workplane("XZ") \
            .moveTo(*points[0]).polyline(points[1:]) \
            .wire()
        return profile
