#!/usr/bin/env python

# The code here should be representative of that in:
#   https://fragmuffin.github.io/cqparts/doc/tutorials/assembly.html

import sys
import os

sys.path.append('../../../../src')

import cadquery
import cqparts
from cqparts.params import *
from cqparts.display import display


# ------------------- Box -------------------

class Box(cqparts.Part):
    length = PositiveFloat(10, doc="box length (along x-axis)")
    width = PositiveFloat(10, doc="box width (along y-axis)")
    height = PositiveFloat(10, doc="box height (along z-axis)")

    def make(self):
        return cadquery.Workplane('XY').box(
            self.length, self.width, self.height,
            centered=(True, True, False),
        )

box = Box(height=5)


# ------------------- Disk -------------------

class Wheel(cqparts.Part):
    radius = PositiveFloat(100, doc="wheel's radius")
    width = PositiveFloat(10, doc="wheel's width")
    def make(self):
        return cadquery.Workplane('XY') \
            .circle(self.radius).extrude(self.width)

wheel = Wheel()


# ------------------- Holy Disk -------------------

class HolyWheel(Wheel):
    hole_diameter = PositiveFloat(20, "diameter for shaft")
    def make(self):
        obj = super(HolyWheel, self).make()
        return obj.faces(">Z").circle(self.hole_diameter / 2) \
            .cutThruAll()

my_wheel = HolyWheel(hole_diameter=50, width=15)


# ------------------- Joined Disk -------------------

class JoinedWheel(cqparts.Part):
    # Parameters
    l_radius = PositiveFloat(100, doc="left wheel's radius")
    l_width = PositiveFloat(10, doc="left wheel's radius")
    r_radius = PositiveFloat(100, doc="right wheel's radius")
    r_width = PositiveFloat(10, doc="right wheel's radius")
    axel_length = PositiveFloat(100, doc="axel length")
    axel_diam = PositiveFloat(10, doc="axel diameter")

    def make(self):
        # Make the axel
        obj = cadquery.Workplane('XY') \
            .circle(self.axel_diam / 2) \
            .extrude(self.axel_length)
        # Make the left and right wheels
        wheel_l = Wheel(radius=self.l_radius, width=self.l_width)
        wheel_r = Wheel(radius=self.r_radius, width=self.r_width)
        # Union them with the axel solid
        obj = obj.union(wheel_l.local_obj)
        obj = obj.union(
            wheel_r.local_obj.mirror('XY') \
                .translate((0, 0, self.axel_length))
        )
        return obj

joined_wheel = JoinedWheel(
    r_radius=80, l_width=20, axel_diam=30,
)
joined_wheel.local_obj


# ------------------- Red Box -------------------

from cqparts.display import render_props, display

class Box(cqparts.Part):
    _render = render_props(template='red', alpha=0.2)
    def make(self):
        return cadquery.Workplane('XY').box(10,10,10)

red_box = Box()


# ------------------- Export -------------------
box.exporter('gltf')('box.gltf', embed=True)
wheel.exporter('gltf')('wheel.gltf', embed=True)
my_wheel.exporter('gltf')('holy-wheel.gltf', embed=True)
joined_wheel.exporter('gltf')('joined-wheel.gltf', embed=True)
red_box.exporter('gltf')('red-box.gltf', embed=True)
