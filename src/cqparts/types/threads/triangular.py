import cadquery

from .base import Thread

class TriangularThread(Thread):
    radius_core = 2.5

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
