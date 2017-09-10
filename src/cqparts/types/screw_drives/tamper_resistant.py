import cadquery
from cadquery import BoxSelector
from math import pi, cos, sqrt

from .base import ScrewDrive, screw_drive


class AcentricWedgesScrewDrive(ScrewDrive):
    count = 4
    width = 0.5
    acentric_radius = None  # defaults to width / 2

    def apply(self, workplane, offset=(0, 0, 0)):
        # Start with a cylindrical pin down the center
        tool = cadquery.Workplane("XY") \
            .circle(self.width / 2).extrude(-self.depth)

        # Create a single blade
        acentric_radius = self.width / 2 if self.acentric_radius is None else self.acentric_radius
        points = [
            (0, 0),
            (0, -self.depth),
            (-self.width / 2, -self.depth),
            (-self.diameter / 2, 0),
        ]
        blade = cadquery.Workplane("XZ").workplane(offset=acentric_radius - (self.width / 2)) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        for i in range(self.count):
            angle = i * (360. / self.count)
            tool = tool.union(
                blade.translate((0, 0, 0)) \
                    .rotate((0, 0, 0), (0, 0, 1), angle)
            )

        return workplane.cut(tool.translate(offset))


@screw_drive('tri_point')
class TripointScrewDrive(AcentricWedgesScrewDrive):
    count = 3
    acentric_radius = 0.0  # yeah, not my best class design, but it works


@screw_drive('torq_set')
class TorqsetScrewDrive(AcentricWedgesScrewDrive):
    count = 4
