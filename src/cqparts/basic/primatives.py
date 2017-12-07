import cadquery

from ..part import Part
from ..params import *
from ..search import register, common_criteria


# basic.primatives registration utility
module_criteria = {
    'lib': 'basic',
    'type': 'primative',
    'module': __name__,
}
_register = common_criteria(**module_criteria)(register)


# ------------- Primative Shapes ------------
@_register(shape='cube')
class Cube(Part):
    size = PositiveFloat(1, doc="length of all sides")
    def make(self):
        return cadquery.Workplane('XY').box(self.size, self.size, self.size)


@_register(shape='sphere')
class Sphere(Part):
    radius = PositiveFloat(1, doc="sphere radius")
    def make(self):
        return cadquery.Workplane('XY').sphere(self.radius)


@_register(shape='cylinder')
class Cylinder(Part):
    radius = PositiveFloat(1, doc="cylinder radius")
    length = PositiveFloat(1, doc="cylinder length")
    def make(self):
        return cadquery.Workplane('XY', origin=(0, 0, self.length/2)) \
            .circle(self.radius).extrude(self.length)


@_register(shape='box')
class Box(Part):
    length = PositiveFloat(1, doc="box dimension along x-axis")
    width = PositiveFloat(1, doc="box dimension along y-axis")
    height = PositiveFloat(1, doc="box dimension along z-axis")
    def make(self):
        return cadquery.Workplane('XY') \
            .box(self.length, self.width, self.height)
