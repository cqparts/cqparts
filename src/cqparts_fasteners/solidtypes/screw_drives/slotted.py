import cadquery
from cqparts.params import *

from .base import ScrewDrive, register


@register(name='slot')
class SlotScrewDrive(ScrewDrive):
    """
    .. image:: /_static/img/screwdrives/slot.png
    """
    width = PositiveFloat(0.5, doc="slot width")

    def make(self):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.depth)
        return tool


@register(name='cross')
class CrossScrewDrive(ScrewDrive):
    """
    .. image:: /_static/img/screwdrives/cross.png
    """
    width = PositiveFloat(0.5, doc="slot width")

    def make(self):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.depth) \
            .faces(">Z") \
            .rect(self.diameter, self.width).extrude(-self.depth)
        return tool
