import cadquery
from math import sqrt, pi, sin, cos
from .base import ScrewDrive, register
from ...utils.geometry import copy
from ...params import *


@register(name='square')
@register(name='robertson')
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

    def make(self):
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

        return tool


@register(name='double_square')
@register(name='2square')
class DoubleSquareScrewDrive(SquareScrewDrive):
    count = IntRange(1, None, 2)


@register(name='tripple_square')
@register(name='3square')
class TrippleSquareScrewDrive(SquareScrewDrive):
    count = IntRange(1, None, 3)
