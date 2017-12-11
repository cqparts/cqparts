
import cadquery
import cqparts

from cqparts.search import register, common_criteria
from cqparts.params import *

from cqparts.constraint.mate import Mate
from cqparts.constraint import LockConstraint, RelativeLockConstraint

from cqparts.display import render_props

# --------------- Basic Parts ----------------
# Parts with the express intent of being concise, and quick to process

register_basic = common_criteria(type='basic')(register)
@register_basic(name='box')
class Box(cqparts.Part):
    """
    Rectangular solid sitting on top of the XY plane, centered on the z-axis
    """
    # Parameters
    length = PositiveFloat(10, doc="box length (along x-axis)")
    width = PositiveFloat(10, doc="box width (along y-axis)")
    height = PositiveFloat(10, doc="box height (along z-axis)")

    _render = render_props(template='red', alpha=0.8)

    def make(self):
        return cadquery.Workplane('XY').box(
            self.length, self.width, self.height,
            centered=(True, True, False),
        )

    @property
    def mate_top(self):
        return Mate((0, 0, self.height))
