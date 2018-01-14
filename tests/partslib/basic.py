
import cadquery
import cqparts

from cqparts.params import *
from cqparts.constraint import Mate
from cqparts.constraint import Fixed, Coincident
from cqparts.utils import CoordSystem


# --------------- Basic Parts ----------------
# Parts with the express intent of being concise, and quick to process

class Box(cqparts.Part):
    """
    Rectangular solid centered on the XY plane, centered on the z-axis
    """
    length = PositiveFloat(1, doc="box length (along x-axis)")
    width = PositiveFloat(1, doc="box width (along y-axis)")
    height = PositiveFloat(1, doc="box height (along z-axis)")

    def make(self):
        return cadquery.Workplane('XY').box(
            self.length, self.width, self.height,
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


class Cylinder(cqparts.Part):
    """
    Cylinder with circular faces parallel with XY plane, length centered on the
    XY plane.
    """
    length = PositiveFloat(1, doc="cylinder length (along z-axis)")
    radius = PositiveFloat(1, doc="cylinder radius")

    def make(self):
        return cadquery.Workplane('XY', origin=(0, 0, -self.length / 2)) \
            .circle(self.radius).extrude(self.length)

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


class CubeStack(cqparts.Assembly):
    """
    2 Cubes, one stacked on top of the other.
    """
    size_a = PositiveFloat(2, doc="size of base cube")
    size_b = PositiveFloat(1, doc="size of top cube")

    def make_components(self):
        return {
            'cube_a': Box(length=self.size_a, width=self.size_a, height=self.size_a),
            'cube_b': Box(length=self.size_b, width=self.size_b, height=self.size_b),
        }

    def make_constraints(self):
        cube_a = self.components['cube_a']
        cube_b = self.components['cube_b']
        return [
            Fixed(cube_a.mate_bottom),
            Coincident(cube_b.mate_bottom, cube_a.mate_top),
        ]

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, self.size_a + self.size_b),
        ))
