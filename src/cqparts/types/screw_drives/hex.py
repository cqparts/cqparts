import cadquery
from math import sqrt, pi, sin, cos
from .base import ScrewDrive, screw_drive
from cqparts.utils import copy


@screw_drive('hex', 'allen')
class HexScrewDrive(ScrewDrive):
    diameter = None
    width = ScrewDrive.diameter * cos(pi / 6)
    count = 1

    def get_diameter(self):
        if self.diameter is None:
            return self.width / cos(pi / 6)
        return self.diameter

    def get_hexagon_vertices(self, diameter):
        """
        Generate the points of a hexagon
        :param diameter: Diameter of hexagon
        :return: list of tuples [(x1, y1), (x2, y2), ... ]
        """
        radius = diameter / 2.0
        points = []
        for i in range(6):
            theta = (i + 0.5) * (pi / 3)
            points.append((cos(theta) * radius, sin(theta) * radius))
        return points

    def apply(self, workplane, offset=(0, 0, 0)):
        diameter = self.get_diameter()

        # Single hex as template
        points = self.get_hexagon_vertices(diameter)
        tool_template = cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(-self.depth)

        # Create tool (rotate & duplicate template)
        tool = copy(tool_template)
        for i in range(1, self.count):
            angle = i * (60.0 / self.count)
            tool = tool.union(
                copy(tool_template).rotate((0, 0, 0), (0, 0, 1), angle)
            )

        return workplane.cut(tool.translate(offset))


@screw_drive('double_hex')
class DoubleHexScrewDrive(HexScrewDrive):
    count = 2
