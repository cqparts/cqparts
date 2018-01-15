
import cadquery

import cqparts
from cqparts.params import *
from cqparts.constraint import Mate
from cqparts.constraint import Fixed, Coincident
from cqparts.utils import CoordSystem



# A greatly simplified version of the tutorial toy car

class Wheel(cqparts.Part):
    width = PositiveFloat(10, doc="wheel width")
    radius = PositiveFloat(20, doc="wheel radius")
    def make(self):
        return cadquery.Workplane('XY').circle(self.radius).extrude(self.width)

    @property
    def mate_connect(self):
        return Mate(self, CoordSystem(normal=(0, 0, 1)))


class Axle(cqparts.Part):
    length = PositiveFloat(50, doc="axle length")
    radius = PositiveFloat(5, doc="axle radius")

    def make(self):
        return cadquery.Workplane('XZ', origin=(0, self.length / 2, 0)) \
            .circle(self.radius).extrude(self.length)

    @property
    def mate_left(self):
        return Mate(self, CoordSystem(
            origin=(0, self.length / 2, 0),
            normal=(0, 1, 0),
        ))

    @property
    def mate_right(self):
        return Mate(self, CoordSystem(
            origin=(0, -self.length / 2, 0),
            normal=(0, -1, 0),
        ))


class AxleAsm(cqparts.Assembly):
    wheel_radius = PositiveFloat(20, doc="wheel radii")
    axle_length = PositiveFloat(50, doc="length of axles")

    def make_components(self):
        return {
            'axle': Axle(length=self.axle_length),
            'wheel_left': Wheel(radius=self.wheel_radius),
            'wheel_right': Wheel(radius=self.wheel_radius),
        }

    def make_constraints(self):
        axle = self.components['axle']
        wheel_left = self.components['wheel_left']
        wheel_right = self.components['wheel_right']
        return [
            Fixed(axle.mate_origin),
            Coincident(wheel_left.mate_connect, axle.mate_left),
            Coincident(wheel_right.mate_connect, axle.mate_right),
        ]


class Chassis(cqparts.Part):
    length = PositiveFloat(100, doc="chassis length")
    width = PositiveFloat(50, doc="chassis length")
    height = PositiveFloat(50, doc="chassis length")
    wheelbase = PositiveFloat(70, doc="distance between axles")

    def make(self):
        return cadquery.Workplane('XY') \
            .box(self.length, self.width, self.height)

    @property
    def mate_front_axle(self):
        return Mate(self, CoordSystem(origin=(self.wheelbase / 2, 0, -self.height / 2)))

    @property
    def mate_back_axle(self):
        return Mate(self, CoordSystem(origin=(-self.wheelbase / 2, 0, -self.height / 2)))


class SimpleCar(cqparts.Assembly):
    width = PositiveFloat(50, doc="chassis width")
    length = PositiveFloat(100, doc="chassis length")
    wheelbase = PositiveFloat(70, doc="distance between axles")
    wheel_radius = PositiveFloat(20, doc="wheel radii")

    def make_components(self):
        return {
            'chassis': Chassis(length=self.length, width=self.width, wheelbase=self.wheelbase),
            'front_wheels': AxleAsm(wheel_radius=self.wheel_radius, axle_length=self.width),
            'back_wheels': AxleAsm(wheel_radius=self.wheel_radius, axle_length=self.width),
        }

    def make_constraints(self):
        chassis = self.components['chassis']
        front = self.components['front_wheels']
        back = self.components['back_wheels']
        return [
            Fixed(chassis.mate_origin),
            Coincident(front.mate_origin, chassis.mate_front_axle),
            Coincident(back.mate_origin, chassis.mate_back_axle),
        ]
