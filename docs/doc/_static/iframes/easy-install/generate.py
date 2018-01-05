#!/usr/bin/env python


# ------------------- Wood Screw -------------------

import cadquery
import cqparts
from cqparts.params import *
from cqparts_fasteners.params import HeadType, DriveType, ThreadType
from cqparts_fasteners.male import MaleFastenerPart
from cqparts.display import display, render_props

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

    _render = render_props(template='aluminium')

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

from math import sin, cos, pi
from cqparts.utils import CoordSystem
from cqparts.constraint import Mate

class Anchor(cqparts.Part):
    # sub-parts
    drive = DriveType(default=('cross', {
        'diameter': 5,
        'width': 1,
        'depth': 2.5,
    }), doc="anchor's drive")

    # scalars
    diameter = PositiveFloat(10, doc="diameter of anchor")
    height = PositiveFloat(5, doc="height of anchor")
    neck_diameter = PositiveFloat(2, doc="width of screw neck")
    head_diameter = PositiveFloat(4, doc="width of screw head")
    spline_point_count = IntRange(4, 200, 10, doc="number of spiral spline points")
    ratio_start = FloatRange(0.5, 0.99, 0.99, doc="radius ratio of wedge start")
    ratio_end = FloatRange(0.01, 0.8, 0.7, doc="radius ratio of wedge end")

    _render = render_props(color=(100, 100, 150))  # dark blue

    @property
    def wedge_radii(self):
        return (
            (self.diameter / 2) * self.ratio_start,  # start radius
            (self.diameter / 2) * self.ratio_end  # end radius
        )

    def make(self):
        obj = cadquery.Workplane('XY') \
            .circle(self.diameter / 2) \
            .extrude(-self.height)

        # neck slot
        obj = obj.cut(
            cadquery.Workplane('XY', origin=(0, 0, -((self.neck_diameter + self.height) / 2))) \
                .moveTo(0, 0) \
                .lineTo(self.diameter / 2, 0) \
                .threePointArc(
                    (0, -self.diameter / 2),
                    (-self.diameter / 2, 0),
                ) \
                .close() \
                .extrude(self.neck_diameter)
        )

        # head slot (forms a circular wedge)
        (start_r, end_r) = self.wedge_radii
        angles_radius = (  # as generator
            (
                (i * (pi / self.spline_point_count)),  # angle
                start_r + ((end_r - start_r) * (i / float(self.spline_point_count)))  # radius
            )
            for i in range(1, self.spline_point_count + 1)  # avoid zero angle
        )
        points = [(cos(a) * r, -sin(a) * r) for (a, r) in angles_radius]
        obj = obj.cut(
            cadquery.Workplane('XY', origin=(0, 0, -((self.head_diameter + self.height) / 2))) \
                .moveTo(start_r, 0) \
                .spline(points) \
                .close() \
                .extrude(self.head_diameter)
        )

        # access port
        obj = obj.cut(
            cadquery.Workplane('XY', origin=(0, 0, -(self.height - self.head_diameter) / 2)) \
                .rect(self.diameter / 2, self.diameter / 2, centered=False) \
                .extrude(-self.height)
        )

        # screw drive
        if self.drive:
            obj = self.drive.apply(obj)

        return obj

    def make_simple(self):
        return cadquery.Workplane('XY') \
            .circle(self.diameter / 2) \
            .extrude(-self.height)

    def make_cutter(self):
        return cadquery.Workplane('XY', origin=(0, 0, -self.height)) \
            .circle(self.diameter / 2) \
            .extrude(self.height + 1000)  # 1m bore depth

    @property
    def mate_screwhead(self):
        (start_r, end_r) = self.wedge_radii
        return Mate(self, CoordSystem(
            origin=(0, -((start_r + end_r) / 2), -self.height / 2),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))


# ------------------- Screw & Anchor -------------------

from cqparts.constraint import Fixed, Coincident

class _Together(cqparts.Assembly):
    def make_components(self):
        return {
            'screw': WoodScrew(neck_exposed=5),
            'anchor': Anchor(height=7),
        }

    def make_constraints(self):
        return [
            Fixed(self.components['screw'].mate_origin),
            Coincident(
                self.components['anchor'].mate_screwhead,
                self.components['screw'].mate_origin,
            ),
        ]


# ------------------- Catalogue -------------------



# ------------------- Catalogue -------------------
# TODO: upon completion of #39


# ------------------- Export / Display -------------------
from cqparts.utils.env import env_name

# ------- Models
screw = WoodScrew()
anchor = Anchor()
together = _Together()

if env_name == 'cmdline':
    screw.exporter('gltf')('screw.gltf')
    anchor.exporter('gltf')('anchor.gltf')
    together.exporter('gltf')('together.gltf')

    display(together)

elif env_name == 'freecad':
    pass  # manually switchable for testing
    #display(screw)
    #display(screw.make_cutter())
    #display(anchor)
    display(together)
