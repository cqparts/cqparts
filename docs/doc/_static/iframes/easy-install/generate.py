#!/usr/bin/env python

import cqparts

# ------------------- Wood Screw -------------------

from math import pi

import cadquery
import cqparts
from cqparts.params import *
from cqparts.fasteners.params import HeadType, DriveType, ThreadType
from cqparts.fasteners.male import MaleFastenerPart
from cqparts.display import display

class WoodScrew(MaleFastenerPart):
    # --- override MaleFastenerPart parameters
    # sub-parts
    head = HeadType(default=('cheese', {
        'diameter': 4,
        'height': 2,
    }), doc="screw's head")
    drive = DriveType(default=('phillips', {
        'diameter': 3.5,
        'depth': 2.5,
        'width': 0.5,
    }), doc="screw's drive")
    thread = ThreadType(default=('triangular', {
        'diameter': 5,  # outer
        'diameter_core': 4.3,  # inner
        'pitch': 2,
        'angle': 30,
    }), doc="screw's thread")

    # scalars
    neck_diam = PositiveFloat(2, doc="neck diameter")
    neck_length = PositiveFloat(40, doc="length from base of head to end of neck")
    length = PositiveFloat(50, doc="length from base of head to end of thread")

    # --- parameters unique for this class
    neck_exposed = PositiveFloat(2, doc="length of neck exposed below head")
    bore_diam = PositiveFloat(6, doc="diameter of screw's bore")

    def initialize_parameters(self):
        super(WoodScrew, self).initialize_parameters()

    def make(self):
        screw = super(WoodScrew, self).make()

        # add bore cylinder
        bore = cadquery.Workplane('XY', origin=(0, 0, -self.neck_length)) \
            .circle(self.bore_diam / 2) \
            .extrude(self.neck_length - self.neck_exposed)
        # cut out sides from bore so it takes less material
        for angle in [i * (360 / 3) for i in range(3)]:
            slice_obj = cadquery.Workplane(
                'XY',
                origin=(self.bore_diam / 2, 0, -(self.neck_exposed + 2))
            ).circle(self.bore_diam / 3) \
                .extrude(-(self.neck_length - self.neck_exposed - 4)) \
                .rotate((0,0,0), (0,0,1), angle)
            bore = bore.cut(slice_obj)
        screw = screw.union(bore)

        return screw

    def make_cutter(self):
        # we won't use MaleFastenerPart.make_cutter() because it
        # implements an access hole that we don't need.
        cutter = cadquery.Workplane('XY') \
            .circle(self.bore_diam / 2) \
            .extrude(-self.neck_length)
        cutter = cutter.union(
            self.thread.make_pilothole_cutter().translate((
                0, 0, -self.length
            ))
        )
        return cutter

    def make_simple(self):
        # in this case, the cutter solid serves as a good simplified
        # model of the screw.
        return self.make_cutter()


# ------------------- Anchor -------------------

class Anchor(cqparts.Part):
    # sub-parts
    drive = DriveType(default=('cross', {
        'diameter': 5,
        'width': 1,
    }), doc="anchor's drive")

    # scalars
    diameter = PositiveFloat(10, doc="diameter of anchor")
    height = PositiveFloat(5, doc="height of anchor")
    neck_diameter = PositiveFloat(2.5, doc="")






# ------------------- Export / Display -------------------
from cqparts.utils.env import env_name

# ------- Models
screw = WoodScrew()
anchor = Anchor()

if env_name == 'cmdline':
    screw.exporter('gltf')('screw.gltf')
    anchor.exporter('gltf')('anchor.gltf')

elif env_name == 'freecad':
    pass  # manually switchable for testing
    display(screw)
    display(screw.make_cutter())
    #display(anchor)
