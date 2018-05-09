

import cadquery as cq

import cqparts
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

#from cqparts.cqparts_fasteners import bolts


class Axle(cqparts.Part):
    length = PositiveFloat(24, doc="axle length")
    diam = PositiveFloat(5, doc="axle diameter")

    def make(self):
        ax = cq.Workplane("XY").circle(self.diam/2).extrude(self.length).faces(">Z").chamfer(0.4)
        return ax

    def get_cutout(self, clearance=0):
        return cq.Workplane('XY', origin=(0, 0, 0)) \
            .circle((self.diam / 2) + clearance) \
            .extrude(10)


class EndCap(cqparts.Part):
    # Parameters
    width = PositiveFloat(42.3, doc="Motor Size")
    height = PositiveFloat(10, doc="End height")
    cham = PositiveFloat(3, doc="chamfer")

    def make(self):
        base = cq.Workplane("XY")\
            .box(self.width, self.width, self.height)\
            .edges("|Z")\
            .chamfer(self.cham)
        return base

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.height/2),
            xDir=(0, 1, 0),
            normal=(0, 0, -1)
            ))

    @property
    def mate_bottom(self):
        return Mate(self,CoordSystem(
            origin=(0,0,-self.height/2),
            xDir=(0,1,0),
            normal=(0,0,1)
            ))


class Stator(cqparts.Part):
    # Parameters
    width = PositiveFloat(40.0,doc="Motor Size")
    height = PositiveFloat(20,doc="stator height")
    cham = PositiveFloat(3,doc="chamfer")

    _render = render_props(color=(50,50,50))

    def make(self):
        base = cq.Workplane("XY").box(self.width, self.width, self.height).edges("|Z").chamfer(self.cham)
        return base

    @property
    def mate_top(self):
        return Mate(self,CoordSystem(
            origin=(0,0,self.height/2),
            xDir=(0,1,0),
            normal=(0,0,1)
            ))

    @property
    def mate_bottom(self):
        return Mate(self,CoordSystem(
            origin=(0,0,-self.height/2),
            xDir=(0,1,0),
            normal=(0,0,1)
            ))


class StepperMount(EndCap):
    spacing = PositiveFloat(31, doc="hole spacing")
    hole_size = PositiveFloat(3, doc="hole size")
    boss = PositiveFloat(22, doc="boss size")
    boss_height = PositiveFloat(2, doc="boss_height")

    def make(self):
        obj = super(StepperMount, self).make()
        obj.faces(">Z").workplane() \
            .rect(self.spacing, self.spacing, forConstruction=True)\
            .vertices() \
            .hole(self.hole_size)
        obj.faces(">Z").workplane()\
            .circle(self.boss/2).extrude(2)
        return obj


class Back(EndCap):
    spacing = PositiveFloat(31, doc="hole spacing")
    hole_size = PositiveFloat(3, doc="hole size")

    def make(self):
        obj = super(Back, self).make()
        obj.faces(">Z").workplane() \
            .rect(self.spacing, self.spacing, forConstruction=True)\
            .vertices() \
            .hole(self.hole_size)
        return obj


class Stepper(cqparts.Assembly):
    width = PositiveFloat(42.3)
    height = PositiveFloat(50)
    hole_spacing = PositiveFloat(31.0)
    hole_size = PositiveFloat(3)
    boss_size = PositiveFloat(22)
    axle_diam = PositiveFloat(5)
    axle_length = PositiveFloat(22)

    def make_components(self):
        sec = self.height / 6
        return {
            'topcap': StepperMount(
                width=self.width,
                height=sec,
                spacing=self.hole_spacing,
                hole_size=self.hole_size,
                boss=self.boss_size
            ),
            'stator': Stator(width=self.width-3, height=sec*4),
            'botcap': Back(width=self.width, height=sec),
            'axle': Axle(length=self.axle_length, diam=self.axle_diam)
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
            Fixed(self.components['axle'].mate_origin),
            ]

    def apply_cutout(self):
        axle = self.components['axle']
        top = self.components['topcap']
        local_obj = top.local_obj
        local_obj = local_obj.cut(axle.get_cutout(clearance=0.5))

    def make_alterations(self):
        self.apply_cutout()

s = Stepper()
# #s = Axle()
display(s)
