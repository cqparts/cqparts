import cadquery
from math import sqrt, pi, sin, cos
from .base import ScrewDrive, screw_drive
from ...utils import copy
from ...params import *


@screw_drive('square', 'robertson')
class SquareScrewDrive(ScrewDrive):
    width = PositiveFloat(None)
    count = IntRange(1, None, 1)

    def initialize_parameters(self):
        super(SquareScrewDrive, self).initialize_parameters()
        if self.width is None:
            self.width = self.diameter / sqrt(2)
        else:
            # Set diameter from square's width (ignore given diameter)
            self.diameter = self.width / cos(pi / 6)

    def apply(self, workplane, offset=(0, 0, 0)):
        (dX, dY, dZ) = offset

        # Single square as template
        tool_template = cadquery.Workplane("XY") \
            .rect(self.width, self.width).extrude(-self.depth)

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
    count = IntRange(1, None, 2)


@screw_drive('tripple_square', '3square')
class TrippleSquareScrewDrive(SquareScrewDrive):
    count = IntRange(1, None, 3)
