import cadquery
from math import sqrt, pi, sin, cos
from .base import ScrewDrive, screw_drive
from cqparts.utils import copy

@screw_drive('square', 'robertson')
class SquareScrewDrive(ScrewDrive):
    width = None
    count = 1

    def get_width(self):
        if self.width is None:
            return self.diameter / sqrt(2)
        return self.width

    def apply(self, workplane, offset=(0, 0, 0)):
        (dX, dY, dZ) = offset
        width = self.get_width()

        # Single square as template
        tool_template = cadquery.Workplane("XY") \
            .rect(width, width).extrude(-self.depth)

        # Create tool (rotate & duplicate template)
        tool = copy(tool_template)
        for i in range(1, self.count):
            angle = i * (90.0 / self.count)
            tool = tool.union(
                copy(tool_template).rotate((0, 0, 0), (0, 0, 1), angle)
            )

        return workplane.cut(tool.translate(offset))


@screw_drive('double_square', '2square')
class DoubleSquareScrewDrive(SquareScrewDrive):
    count = 2


@screw_drive('tripple_square', '3square')
class TrippleSquareScrewDrive(SquareScrewDrive):
    count = 3
