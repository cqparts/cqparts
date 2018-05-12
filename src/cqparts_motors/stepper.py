
# cqparts motors
# 2018 Simon Kirkby obeygiantrobot@gmail.com

# stepper motor generic

# TODO 
# need a cutout for mounting
# even 4 fasteners so it auto mounts to whatever it is parented to.

import cadquery as cq

import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.display import render_props
from cqparts.utils.geometry import CoordSystem

import shaft

class _EndCap(cqparts.Part):
    # Parameters
    width = PositiveFloat(42.3, doc="Motor Size")
    length = PositiveFloat(10, doc="End length")
    cham = PositiveFloat(3, doc="chamfer")

    def make(self):
        base = cq.Workplane("XY")\
            .box(self.width, self.width, self.length)\
            .edges("|Z")\
            .chamfer(self.cham)
        return base

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, -1)
            ))

    @property
    def mate_bottom(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))


class _Stator(cqparts.Part):
    # Parameters
    width = PositiveFloat(40.0, doc="Motor Size")
    length = PositiveFloat(20, doc="stator length")
    cham = PositiveFloat(3, doc="chamfer")

    _render = render_props(color=(50, 50, 50))

    def make(self):
        base = cq.Workplane("XY")\
            .box(self.width, self.width, self.length)\
            .edges("|Z")\
            .chamfer(self.cham)
        return base

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))

    @property
    def mate_bottom(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))


class _StepperMount(_EndCap):
    spacing = PositiveFloat(31, doc="hole spacing")
    hole_size = PositiveFloat(3, doc="hole size")
    boss = PositiveFloat(22, doc="boss size")
    boss_length = PositiveFloat(2, doc="boss_length")

    def make(self):
        obj = super(_StepperMount, self).make()
        obj.faces(">Z").workplane() \
            .rect(self.spacing, self.spacing, forConstruction=True)\
            .vertices() \
            .hole(self.hole_size)
        obj.faces(">Z").workplane()\
            .circle(self.boss/2).extrude(self.boss_length)
        return obj


class _Back(_EndCap):
    spacing = PositiveFloat(31, doc="hole spacing")
    hole_size = PositiveFloat(3, doc="hole size")

    def make(self):
        obj = super(_Back, self).make()
        obj.faces(">Z").workplane() \
            .rect(self.spacing, self.spacing, forConstruction=True)\
            .vertices() \
            .hole(self.hole_size)
        return obj


class Stepper(cqparts.Assembly):

    # Shaft type
    shaft_type = shaft.Shaft

    width = PositiveFloat(42.3)
    length = PositiveFloat(50)
    hole_spacing = PositiveFloat(31.0)
    hole_size = PositiveFloat(3)
    boss_size = PositiveFloat(22)
    boss_length = PositiveFloat(2)

    shaft_diam = PositiveFloat(5)
    shaft_length = PositiveFloat(24)

    def make_components(self):
        sec = self.length / 6
        return {
            'topcap': _StepperMount(
                width=self.width,
                length=sec,
                spacing=self.hole_spacing,
                hole_size=self.hole_size,
                boss=self.boss_size
            ),
            'stator': _Stator(width=self.width-3, length=sec*4),
            'botcap': _Back(
                width=self.width,
                length=sec,
                spacing=self.hole_spacing,
                hole_size=self.hole_size,
            ),
            'shaft': self.shaft_type(
                length=self.shaft_length,
                diam=self.shaft_diam)
            }

    def make_constraints(self):
        return [
            Fixed(self.components['topcap'].mate_origin),
            Coincident(
                self.components['stator'].mate_bottom,
                self.components['topcap'].mate_top
            ),
            Coincident(
                self.components['botcap'].mate_bottom,
                self.components['stator'].mate_top
            ),
            Fixed(
                self.components['shaft'].mate_origin,
                CoordSystem(
                    (0, 0, self.length/8-self.boss_length),
                    (1, 0, 0),
                    (0, 0, 1)
                )
            )
            ]

    def apply_cutout(self):
        shaft = self.components['shaft']
        top = self.components['topcap']
        local_obj = top.local_obj
        local_obj = local_obj.cut(shaft.get_cutout(clearance=0.5))

    def make_alterations(self):
        self.apply_cutout()

# Sized motors , build into collection
# http://www.osmtec.com/stepper_motors.htm is a good reference
# sizes 8, 11, 14, 16, 17, 23, 24, 34, 42
# s = Stepper()
# s.serialize_parameters().keys()
#['shaft_length', 'hole_spacing', 'hole_size', 'length', 'width', 'boss_size', 'shaft_diam', 'boss_length']

_NemaSizes = {
    8 :  [10.0, 15.4, 2.0, 28.0, 20.3, 16.0, 4.0, 1.5],
    11 : [20.0, 23.0, 2.5, 31.5, 28.2, 22.0, 4.0, 2.0],
    14 : [24.0, 26.0, 3.0, 28.0, 35.2, 22.0, 5.0, 2.0],
    17 : [24.0, 31.0, 3.0, 50.0, 42.0, 22.0, 5.0, 2.0],
    23 : [21.0, 47.0, 5.0, 56.0, 57.0, 38.0, 6.35, 1.6],
    # finish sizes
}

def NEMA(size):
    if _NemaSizes.has_key(size):
        return _GetNEMASize(_NemaSizes[size])
    else:
        raise 

def _GetNEMASize(v):
    s = Stepper(
        shaft_length=v[0],
        hole_spacing=v[1],
        hole_size=v[2],
        length=v[3],
        width=v[4],
        boss_size=v[5],
        shaft_diam=v[6],
        boss_length=v[7]
    )
    return s

def _GenSteppers():
    sizes = {}
    for size,values in _NemaSizes.items():
        sizes[size] = _GetNEMASize(values)
    return sizes

