import cadquery
from cadquery import BoxSelector
from math import pi, cos
from .base import ScrewDrive, screw_drive


@screw_drive('frearson')
class FrearsonScrewDrive(ScrewDrive):
    width = 0.5
    taper_ratio = 0.8

    def apply(self, workplane, offset=(0, 0, 0)):
        (dX, dY, dZ) = offset
        tool = cadquery.Workplane("XY").workplane(offset=dZ).center(dX, dY) \
            .rect(self.width, self.diameter).workplane(offset=-self.depth) \
            .rect(self.width * taper_ratio, self.width * taper_ratio).loft() \
            .faces(">Z") \
            .rect(self.diameter, self.width).workplane(offset=-self.depth) \
            .rect(self.width * taper_ratio, self.width * taper_ratio).loft() \
        return workplane.cut(tool)


@screw_drive('phillips')
class PhillipsScrewDrive(ScrewDrive):
    width = 0.5
    chamfer = 0.2

    def apply(self, workplane, offset=(0, 0, 0)):
        (dX, dY, dZ) = offset
        tool = cadquery.Workplane("XY").workplane(offset=dZ).center(dX, dY) \
            .rect(self.width, self.diameter).workplane(offset=-self.depth) \
            .rect(self.width, self.width).loft() \
            .faces(">Z") \
            .rect(self.diameter, self.width).workplane(offset=-self.depth) \
            .rect(self.width, self.width).loft() \
            .edges(BoxSelector(
                (self.width, self.width, 0),
                (-self.width, -self.width, -self.depth)
            )).chamfer(self.chamfer)
        return workplane.cut(tool)
