import cadquery
from .base import ScrewDrive, screw_drive


@screw_drive('slot')
class SlotScrewDrive(ScrewDrive):
    width = 0.5

    def apply(self, workplane, offest=(0, 0, 0)):
        (dX, dY, dZ) = offset
        tool = cadquery.Workplane("XY").workplane(offset=dZ).center(dX, dY) \
            .rect(self.width, self.diameter).extrude(-self.depth) \
        return workplane.cut(tool)


@screw_drive('cross')
class CrossScrewDrive(ScrewDrive):
    width = 0.5

    def apply(self, workplane, offset=(0, 0, 0)):
        (dX, dY, dZ) = offset
        tool = cadquery.Workplane("XY").workplane(offset=dZ).center(dX, dY) \
            .rect(self.width, self.diameter).extrude(-self.depth) \
            .faces(">Z") \
            .rect(self.diameter, self.width).extrude(-self.depth) \
        return workplane.cut(tool)
