import six
from math import tan
from math import radians
import logging

import cadquery

from ..part import Part, Assembly
from ..solidtypes import threads
from ..params import *

from .utils import Evaluator, Selector, Applicator
from .params import HeadType, DriveType, ThreadType


log = logging.getLogger(__name__)


# ----------------- Fastener Components ---------------
# eg: for a nut & bolt, the nut is a component, the bolt is a component,
# and the combination of the two is a Fastener.
class FastenerMalePart(Part):
    r"""
    Male fastener part; with an external thread

    ::

                                   _________  __ head height
                                  | \/   \/ |
                z=0 __ _________  |_/\___/\_| __ z=0 (on x/y plane, +z is up)
                       \       /    |     |
        head height __  \     /     |     |
                         |   |      |     |   __ neck length (excludes taper)
                        -\---/-     -\---/-
                        -|---|-     -|---|-
                        -|---|-     -|---|-
                        -|---|-     -|---|-   __ tip (length from bottom)
                        -\---/-     -\---/-
                          \_/         \_/     __ length

    .. warning::

        Tip thread tapering has not been implemented, except in
        the simplified model.

    """

    length = PositiveFloat(4.5, doc="length from xy plane to tip")
    neck_length = PositiveFloat(0, doc="length of neck, includes taper")
    neck_taper = FloatRange(0, 90, 30, doc="angle of neck's taper (0 is parallel with neck)")
    neck_diam = PositiveFloat(None, doc="neck radius, defaults to thread's outer radius")
    tip_length = PositiveFloat(0, doc="length of taper on a pointed tip")
    tip_diameter = PositiveFloat(None, doc="diameter of tip's point")

    head = HeadType(
        default=('pan', {
            'diameter': 5.2,
            'height': 2.0,
            'fillet': 1.0,
        }),
        doc="head type and parameters",
    )
    drive = DriveType(
        default=('phillips', {
            'diameter': 3,
            'depth': 2.0,
            'width': 0.6,
        }),
        doc="screw drive type and parameters",
    )
    thread = ThreadType(
        default=('iso262', {  # M3
            'diameter': 3.0,
            'pitch': 0.35,
        }),
        doc="thread type and parameters",
    )

    def initialize_parameters(self):
        (inner_radius, outer_radius) = self.thread.get_radii()
        if self.neck_length and (not self.neck_diam):
            self.neck_diam = outer_radius * 2
        if self.tip_length and (self.tip_diameter is None):
            self.tip_diameter = outer_radius / 5

        # thread offset ensures a small overlap with mating surface
        thread_offset = 0
        if not self.neck_length:
            thread_offset = [face_z_offset - 0.01, -0.01, 0.01][cmp(face_z_offset, 0)+1]

        # build Thread (and union it to to the head)
        if self.length <= self.neck_length:
            raise ValueError("screw's neck (%g) is longer than the thread (%g)" % (
                self.neck_length, self.length,
            ))
        # (change thread's length before building... not the typical flow, but
        #  it works all the same)
        self.thread.length = (self.length - self.neck_length) + thread_offset
        self.local_obj = None  # clear to force build after parameter change

    def make(self):
        face_z_offset = self.head.get_face_offset()[2]

        # build Head
        obj = self.head.make()
        # (screw drive indentation is made last)

        # build neck
        (inner_radius, outer_radius) = self.thread.get_radii()
        if self.neck_length:
            # neck
            neck = cadquery.Workplane(
                'XY', origin=(0, 0, -self.neck_length)
            ).circle(self.neck_diam / 2).extrude(self.neck_length)
            obj = obj.union(neck)

            # neck -> taper to thread's inner radius
            taper_length = 0
            if 0 < self.neck_taper < 90:
                taper_length = ((self.neck_diam / 2) - inner_radius) / tan(radians(self.neck_taper))

            neck_taper = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(
                    radius1=(self.neck_diam / 2),
                    radius2=inner_radius,
                    height=taper_length,
                    dir=cadquery.Vector(0,0,-1),
                )).translate((0, 0, -self.neck_length))
            )
            obj = obj.union(neck_taper)

        # build thread
        thread = self.thread.local_obj.translate((0, 0, -self.length))
        obj = obj.union(thread)

        # Sharpen to a point
        if self.tip_length:
            # create "cutter" tool shape
            tip_cutter = cadquery.Workplane('XY').box(
                (outer_radius * 2) + 10, (outer_radius * 2) + 10, self.tip_length,
                centered=(True, True, False),
            )
            tip_template = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(
                    radius1=(self.tip_diameter / 2),
                    radius2=outer_radius,
                    height=self.tip_length,
                    dir=cadquery.Vector(0,0,1),
                ))
            )
            tip_cutter = tip_cutter.cut(tip_template)

            # move & cut
            obj.cut(tip_cutter.translate((0, 0, -self.length)))

        # apply screw drive (if there is one)
        if self.drive:
            obj = self.drive.apply(obj,
                offset=self.head.get_face_offset()
            )

        return obj

    #def make_simple(self):
    #    pass

    def make_cutter(self):
        # head
        obj = self.head.make_cutter()

        # neck
        if self.neck_length:
            neck = cadquery.Workplane(
                'XY', origin=(0, 0, -self.neck_length)
            ).circle(self.neck_diam / 2).extrude(self.neck_length)
            obj = obj.union(neck)

        # thread (pilot hole)
        pilot_hole = self.thread.make_pilothole_cutter() \
            .translate((0, 0, -self.length))
        obj = obj.union(pilot_hole)

        return obj


class FastenerFemale(Part):
    """
    Female fastener part; with an internal thread

    For a *nut* and *bolt*:

    * *nut* : female
    * *bolt* : male
    """


# ----------------- Fastener Base ---------------
class Fastener(Assembly):
    # Parameters
    parts = PartsList(doc="List of parts being fastened")

    # Class assignment
    Evaluator = Evaluator
    Selector = Selector
    Applicator = Applicator

    def make_components(self):
        # --- Run evaluation
        self.evaluation = self.Evaluator(
            parts=self.parts,
            location=self.world_coords,
        )

        # --- Select fastener (based on evaluation)
        self.selector = self.Selector(
            evaluation=self.evaluation,
        )

        # --- add components
        return self.selector.components

    def make_constraints(self):
        # --- Create mates from evaluation results
        return self.selector.constraints

    def make_alterations(self):
        self.applicator = self.Applicator(
            evaluation=self.evaluation,
            selector=self.selector,
        )
        self.applicator.apply()
