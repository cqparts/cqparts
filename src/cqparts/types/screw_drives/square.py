import cadquery
from math import sqrt, pi, sin, cos,
from .base import ScrewDrive, screw_drive


@screw_drive('square', 'robertson')
class SquareScrewDrive(ScrewDrive):
    width = None
    count = 1

    def get_width(self):
        if self.width is None:
            return self.diamter / sqrt(2)
        return self.width

    def apply(self, workplane, offest=(0, 0, 0)):
        (dX, dY, dZ) = offset
        width = self.get_width()

        tools = []
        for i in range(self.count):
            angle = i * (90.0 / self.count)
            tools.append(
                cadquery.Workplane("XY").workplane(offset=dZ).center(dX, dY) \
                    .rect(width, width).extrude(-self.depth) \
                    .rotate((0,0,0), (0,0,1), angle)
            )

        for tool in tools:
            workplane.cut(tool)

        return workplane


@screw_drive('double_square')
class DoubleSquareScrewDrive(SquareScrewDrive):
    count = 2


@screw_drive('tripple_square')
class TrippleSquareScrewDrive(SquareScrewDrive):
    count = 3
