import cadquery
from cadquery import BoxSelector
from math import pi, cos, sqrt

from .base import ScrewDrive, screw_drive
from cqparts.utils import intersect


@screw_drive('frearson')
class FrearsonScrewDrive(ScrewDrive):
    width = 0.5

    def apply(self, workplane, offset=(0, 0, 0)):
        points = [
            (self.diameter / 2., 0),
            (self.width / 2., -self.depth),
            (-self.width / 2., -self.depth),
            (-self.diameter / 2., 0),
        ]
        tool_cross_x = cadquery.Workplane("XZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)
        tool_cross_y = cadquery.Workplane("YZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        tool = tool_cross_x.union(tool_cross_y)
        return workplane.cut(tool.translate(offset))


@screw_drive('phillips')
class PhillipsScrewDrive(ScrewDrive):
    width = 0.5
    chamfer = 0.2

    def apply(self, workplane, offset=(0, 0, 0)):
        #(dX, dY, dZ) = offset
        #tool1 = cadquery.Workplane("XY").workplane(offset=dZ).center(dX, dY) \
        #    .rect(self.width, self.diameter).workplane(offset=-self.depth) \
        #    .rect(self.width, self.width).loft(ruled=True) \
        #    .faces(">Z") \
        #    .rect(self.diameter, self.width).workplane(offset=-self.depth) \
        #    .rect(self.width, self.width).loft(ruled=True)

        # Frearson style cross from center
        points = [
            (self.diameter / 2., 0),
            (self.width / 2., -self.depth),
            (-self.width / 2., -self.depth),
            (-self.diameter / 2., 0),
        ]
        tool_cross_x = cadquery.Workplane("XZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)
        tool_cross_y = cadquery.Workplane("YZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        # Trapezoidal pyramid 45deg rotated cutout of center
        # alternative: lofting 2 squares, but that was taking ~7 times longer to process
        tz_top = 3. * self.width
        tz_base = self.width / sqrt(2)  # to fit inside square at base
        points = [
            (tz_top / 2., 0),
            (tz_base / 2., -self.depth),
            (-tz_base / 2., -self.depth),
            (-tz_top / 2., 0),
        ]
        tool_tzpy1 = cadquery.Workplane("XZ").workplane(offset=-tz_top / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(tz_top)
        tool_tzpy2 = cadquery.Workplane("YZ").workplane(offset=-tz_top / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(tz_top)
        tool_tzpy = intersect(tool_tzpy1, tool_tzpy2) \
            .rotate((0, 0, 0), (0, 0, 1), 45)

        tool = cadquery.Workplane("XY") \
            .union(tool_cross_x) \
            .union(tool_cross_y) \
            .union(tool_tzpy)
        return workplane.cut(tool.translate(offset))
