
import cadquery as cq

import cqparts
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

# base shaft type
class Shaft(cqparts.Part):
    length = PositiveFloat(24, doc="shaft length")
    diam = PositiveFloat(5, doc="shaft diameter")

    _render = render_props(color=(50,255,255))

    def make(self):
        shft = cq.Workplane("XY")\
            .circle(self.diam/2)\
            .extrude(self.length)\
            .faces(">Z")\
            .chamfer(0.4)
        return shft 

    def get_cutout(self, clearance=0):
        return cq.Workplane('XY', origin=(0, 0, 0)) \
            .circle((self.diam / 2) + clearance) \
            .extrude(self.length*2)
