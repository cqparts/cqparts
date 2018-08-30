#!/usr/bin/env python

# The code here should be representative of that in:
#   https://fragmuffin.github.io/cqparts/doc/tutorials/assembly.html

# ------------------- Wheel -------------------

import cadquery
import cqparts
from cqparts.params import *
from cqparts.display import render_props, display

class Wheel(cqparts.Part):
    # Parameters
    width = PositiveFloat(10, doc="width of wheel")
    diameter = PositiveFloat(30, doc="wheel diameter")

    # default appearance
    _render = render_props(template='wood_dark')

    def make(self):
        wheel = cadquery.Workplane('XY') \
            .circle(self.diameter / 2).extrude(self.width)
        hole = cadquery.Workplane('XY') \
            .circle(2).extrude(self.width/2).faces(">Z") \
            .circle(4).extrude(self.width/2)
        wheel = wheel.cut(hole)
        return wheel

    def get_cutout(self, clearance=0):
        # A cylinder with a equal clearance on every face
        return cadquery.Workplane('XY', origin=(0, 0, -clearance)) \
            .circle((self.diameter / 2) + clearance) \
            .extrude(self.width + (2 * clearance))


# ------------------- Axle -------------------

from cqparts.constraint import mate
from cqparts.utils.geometry import CoordSystem

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
    @mate
    def left(self):
        return CoordSystem(
            origin=(0, -self.length / 2, 0),
            xDir=(1, 0, 0), normal=(0, -1, 0),
        )

    @mate
    def right(self):
        return CoordSystem(
            origin=(0, self.length / 2, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        )

    def get_cutout(self, clearance=0):
        return cadquery.Workplane('ZX', origin=(0, -self.length/2 - clearance, 0)) \
            .circle((self.diameter / 2) + clearance) \
            .extrude(self.length + (2 * clearance))


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


# ------------------- Wheel Assembly -------------------

from cqparts.constraint import Fixed, Coincident

class WheeledAxle(cqparts.Assembly):
    wheel = ComponentRef(doc="wheel part")
    axle = ComponentRef(doc="axle part")
    wheel_clearance = PositiveFloat(3, doc="distance between wheel and chassis")

    def make_components(self):
        axle_length = self.axle_track - (self.left_width + self.right_width) / 2
        return {
            'axle': self.axle,
            'left_wheel': self.wheel,
            'right_wheel': self.wheel,
        }

    def make_constraints(self):
        return [
            Fixed(self['axle'].mate('origin'), CoordSystem()),
            Coincident(
                self['left_wheel'].mate('origin'),
                self['axle'].mate('left'),
            ),
            Coincident(
                self['right_wheel'].mate('origin'),
                self['axle'].mate('right'),
            ),
        ]

    def apply_cutout(self, part):
        # Cut wheel & axle from given part
        axle = self.components['axle']
        left_wheel = self.components['left_wheel']
        right_wheel = self.components['right_wheel']
        local_obj = part.local_obj
        local_obj = local_obj \
            .cut((axle.world_coords - part.world_coords) + axle.get_cutout()) \
            .cut((left_wheel.world_coords - part.world_coords) + left_wheel.get_cutout(self.wheel_clearance)) \
            .cut((right_wheel.world_coords - part.world_coords) + right_wheel.get_cutout(self.wheel_clearance))
        part.local_obj = local_obj


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
            Fixed(self.components['chassis'].mate_origin),
            Coincident(
                self.components['front_axle'].mate_origin,
                Mate(self.components['chassis'], CoordSystem((self.wheelbase/2,0,0))),
            ),
            Coincident(
                self.components['rear_axle'].mate_origin,
                Mate(self.components['chassis'], CoordSystem((-self.wheelbase/2,0,0))),
            ),
        ]

    def make_alterations(self, placed_self):
        # cut out wheel wells
        chassis = placed_self['chassis']
        placed_self['front_axle'].apply_cutout(chassis)
        placed_self['rear_axle'].apply_cutout(chassis)


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'toy_car':
    # not run as a module, so display result
    car = Car()
    from cqparts.display import display
    display(car)
