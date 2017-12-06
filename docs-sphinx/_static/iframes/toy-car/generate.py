#!/usr/bin/env python

# The code here should be representative of that in:
#   https://fragmuffin.github.io/cqparts/doc/tutorials/assembly.html

import sys
import os

sys.path.append('../../../../src')

import cadquery
import cqparts
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraints import Mate


def write_file(obj, filename, world=False):
    if isinstance(obj, cqparts.Assembly):
        obj.solve()
        for (name, child) in obj.components.items():
            s = os.path.splitext(filename)
            write_file(child, "%s.%s%s" % (s[0], name, s[1]), world=True)
    else:
        print("exporting: %r" % obj)
        print("       to: %s" % filename)
        with open(filename, 'w') as fh:
            fh.write(obj.get_export_gltf(world=world))


# ------------------- Wheel -------------------

class Wheel(cqparts.Part):
    # Parameters
    width = PositiveFloat(10, doc="width of wheel")
    diameter = PositiveFloat(30, doc="wheel diameter")

    # default appearance
    _render = render_props(template='wood_dark')

    def make(self):
        wheel = cadquery.Workplane('XY') \
            .circle(self.diameter / 2).extrude(self.width)
        cutout = cadquery.Workplane('XY') \
            .circle(2).extrude(self.width/2).faces(">Z") \
            .circle(4).extrude(self.width/2)
        wheel = wheel.cut(cutout)
        return wheel

wheel = Wheel()
write_file(wheel, 'wheel.gltf')


# ------------------- Axle -------------------

class Axle(cqparts.Part):
    # Parameters
    length = PositiveFloat(50, doc="axle length")
    diameter = PositiveFloat(10, doc="axle diameter")

    # default appearance
    _render = render_props(color=(50, 50, 50))  # dark grey

    def make(self):
        axle = cadquery.Workplane('ZX', origin=(0, -self.length/2, 0)) \
            .circle(self.diameter / 2).extrude(self.length)
        cutout = cadquery.Workplane('ZX', origin=(0, -self.length/2, 0)) \
            .circle(1.5).extrude(10)
        axle = axle.cut(cutout)
        cutout = cadquery.Workplane('XZ', origin=(0, self.length/2, 0)) \
            .circle(1.5).extrude(10)
        axle = axle.cut(cutout)
        return axle

    # wheel mates, assuming they rotate around z-axis
    @property
    def mate_left(self):
        return Mate(
            origin=(0, -self.length / 2, 0),
            xDir=(1, 0, 0), normal=(0, -1, 0),
        )

    @property
    def mate_right(self):
        return Mate(
            origin=(0, self.length / 2, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        )
axle = Axle()
write_file(axle, 'axle.gltf')


# ------------------- Chassis -------------------

class Chassis(cqparts.Part):
    # Parameters
    width = PositiveFloat(50, doc="chassis width")

    _render = render_props(template='wood_light')

    def make(self):
        points = [  # chassis outline
            (-60,0),(-60,22),(-47,23),(-37,40),
            (5,40),(23,25),(60,22),(60,0),
        ]
        return cadquery.Workplane('XZ', origin=(0,self.width/2,0)) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

chassis = Chassis()
write_file(chassis, 'chassis.gltf')


# ------------------- Wheel Assembly -------------------

from cqparts.constraints import LockConstraint, RelativeLockConstraint

class WheeledAxle(cqparts.Assembly):
    left_width = PositiveFloat(7, doc="left wheel width")
    right_width = PositiveFloat(7, doc="right wheel width")
    left_diam = PositiveFloat(25, doc="left wheel diameter")
    right_diam = PositiveFloat(25, doc="right wheel diameter")
    axle_diam = PositiveFloat(8, doc="axel diameter")
    axle_track = PositiveFloat(50, doc="distance between wheel tread midlines")

    def make_components(self):
        axel_length = self.axle_track - (self.left_width + self.right_width) / 2
        return {
            'axle': Axle(length=axel_length, diameter=self.axle_diam),
            'left_wheel': Wheel(
                 width=self.left_width, diameter=self.left_diam,
            ),
            'right_wheel': Wheel(
                 width=self.right_width, diameter=self.right_diam,
            ),
        }

    def make_constraints(self):
        return [
            LockConstraint(self.components['axle'], Mate()),
            RelativeLockConstraint(
                self.components['left_wheel'],
                self.components['axle'].mate_left,
                self.components['axle']
            ),
            RelativeLockConstraint(
                self.components['right_wheel'],
                self.components['axle'].mate_right,
                self.components['axle']
            ),
        ]

wheeled_axle = WheeledAxle(right_width=2)
write_file(wheeled_axle, 'wheel-assembly.gltf')

print(wheeled_axle.tree_str(name='wheel_assembly'))


# ------------------- Car Assembly -------------------

class Car(cqparts.Assembly):
    # Parameters
    wheelbase = PositiveFloat(70, "distance between front and rear axles")
    axle_track = PositiveFloat(60, "distance between tread midlines")
    # wheels
    wheel_width = PositiveFloat(10, doc="width of all wheels")
    front_wheel_diam = PositiveFloat(30, doc="front wheel diameter")
    rear_wheel_diam = PositiveFloat(30, doc="rear wheel diameter")
    axle_diam = PositiveFloat(10, doc="axle diameter")

    def make_components(self):
        return {
            'chassis': Chassis(width=self.axle_track),
            'front_axle': WheeledAxle(
                left_width=self.wheel_width,
                right_width=self.wheel_width,
                left_diam=self.front_wheel_diam,
                right_diam=self.front_wheel_diam,
                axle_diam=self.axle_diam,
                axle_track=self.axle_track,
            ),
            'rear_axle': WheeledAxle(
                left_width=self.wheel_width,
                right_width=self.wheel_width,
                left_diam=self.rear_wheel_diam,
                right_diam=self.rear_wheel_diam,
                axle_diam=self.axle_diam,
                axle_track=self.axle_track,
            ),
        }

    def make_constraints(self):
        return [
            LockConstraint(self.components['chassis'], Mate()),
            RelativeLockConstraint(
                self.components['front_axle'],
                Mate((self.wheelbase/2,0,0)),
                self.components['chassis'],
            ),
            RelativeLockConstraint(
                self.components['rear_axle'],
                Mate((-self.wheelbase/2,0,0)),
                self.components['chassis'],
            ),
        ]

car = Car()
write_file(car, 'car.gltf')

print(car.tree_str(name='car'))
