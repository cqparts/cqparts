
import cadquery
import cqparts

from cqparts.params import *
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem


# --------------- Basic Parts ----------------
# Parts with the express intent of being concise, and quick to process

class Box(cqparts.Part):
    """
    Rectangular solid centered on the XY plane, centered on the z-axis
    """
    # Parameters
    length = PositiveFloat(10, doc="box length (along x-axis)")
    width = PositiveFloat(10, doc="box width (along y-axis)")
    height = PositiveFloat(10, doc="box height (along z-axis)")

    def make(self):
        return cadquery.Workplane('XY').box(
            self.length, self.width, self.height,
            centered=(True, True, True),
        )

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, self.height / 2)
        ))

    @property
    def mate_bottom(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.height / 2),
        ))
