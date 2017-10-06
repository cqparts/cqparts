import cadquery
from .base import ScrewDrive, screw_drive

from ...params import *


@screw_drive('slot')
class SlotScrewDrive(ScrewDrive):
    width = PositiveFloat(0.5)

    def apply(self, workplane, offset=(0, 0, 0)):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.depth)
        return workplane.cut(tool.translate(offset))


@screw_drive('cross')
class CrossScrewDrive(ScrewDrive):
    width = PositiveFloat(0.5)

    def apply(self, workplane, offset=(0, 0, 0)):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.depth) \
            .faces(">Z") \
            .rect(self.diameter, self.width).extrude(-self.depth)
        return workplane.cut(tool.translate(offset))
