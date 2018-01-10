#!/usr/bin/env python


import cadquery
import logging
cadquery.freecad_impl.console_logging.enable(logging.INFO)


# ------------------- Wood Screw -------------------

import cadquery
import cqparts
from cqparts.params import *
from cqparts_fasteners.params import HeadType, DriveType, ThreadType
from cqparts_fasteners.male import MaleFastenerPart
from cqparts.display import display, render_props
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem


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
        cutter = cadquery.Workplane('XY', origin=(0, 0, self.head.height)) \
            .circle(self.bore_diam / 2) \
            .extrude(-(self.neck_length + self.head.height))
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

    @property
    def mate_threadstart(self):
        return Mate(self, CoordSystem(origin=(0, 0, -self.neck_length)))


# ------------------- Anchor -------------------

from math import sin, cos, pi

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

        # neck slot : eliminate screw neck interference
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

        # head slot : form a circular wedge with remaining material
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

        # access port : remove a quadrant to alow screw's head through
        obj = obj.cut(
            cadquery.Workplane('XY', origin=(0, 0, -(self.height - self.head_diameter) / 2)) \
                .rect(self.diameter / 2, self.diameter / 2, centered=False) \
                .extrude(-self.height)
        )

        # screw drive : to apply torque to anchor for installation
        if self.drive:
            obj = self.drive.apply(obj)  # top face is on origin XY plane

        return obj

    def make_simple(self):
        # Just return the core cylinder
        return cadquery.Workplane('XY') \
            .circle(self.diameter / 2) \
            .extrude(-self.height)

    def make_cutter(self):
        # A solid to cut away from another; makes room to install the anchor
        return cadquery.Workplane('XY', origin=(0, 0, -self.height)) \
            .circle(self.diameter / 2) \
            .extrude(self.height + 1000)  # 1m bore depth

    @property
    def mate_screwhead(self):
        # The location of the screwhead in it's theoretical tightened mid-point
        #   (well, not really, but this is just a demo)
        (start_r, end_r) = self.wedge_radii
        return Mate(self, CoordSystem(
            origin=(0, -((start_r + end_r) / 2), -self.height / 2),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))

    @property
    def mate_center(self):
        # center of object, along screw's rotation axis
        return Mate(self, CoordSystem(origin=(0, 0, -self.height / 2)))

    @property
    def mate_base(self):
        # base of object (for 3d printing placement, maybe)
        return Mate(self, CoordSystem(origin=(0, 0, -self.height)))


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


# ------------------- WoodPanel -------------------

class WoodPanel(cqparts.Part):
    thickness = PositiveFloat(15, doc="thickness of panel")
    width = PositiveFloat(100, doc="panel width")
    length = PositiveFloat(100, doc="panel length")

    _render = render_props(template='wood')  # wooden

    def make(self):
        return cadquery.Workplane('XY') \
            .box(self.length, self.width, self.thickness)

    @property
    def mate_end(self):
        # center of +x face
        return Mate(self, CoordSystem(
            origin=(self.length / 2, 0, 0),
            xDir=(0, 0, -1),
            normal=(-1, 0, 0),
        ))

    def get_mate_edge(self, thickness):
        return Mate(self, CoordSystem(
            origin=((self.length / 2) - (thickness / 2), 0, self.thickness / 2)
        ))


# ------------------- Fastener -------------------

from cqparts_fasteners import Fastener
from cqparts_fasteners.utils import VectorEvaluator, Selector, Applicator

from cqparts.constraint import Fixed, Coincident


class EasyInstallFastener(Fastener):
    # The origin of the evaluation is to be the target center for the anchor.
    Evaluator = VectorEvaluator

    class Selector(Selector):
        def get_components(self):
            anchor = Anchor(
                height=10,
            )

            # --- Define the screw's dimensions
            # Get distance from anchor's center to screwhead's base
            #   (we'll call that the "anchor's slack")
            v_rel_center = anchor.mate_center.local_coords.origin
            v_rel_screwhead = anchor.mate_screwhead.local_coords.origin
            anchor_slack = abs(v_rel_screwhead - v_rel_center)
            # The slack is along the evaluation vector, which is the same
            # as the woodscrew's axis of rotation.

            # Find the screw's neck length
            #   This will be the length of all but the last evaluator effect,
            #   minus the anchor's slack.
            effect_length = abs(self.evaluator.eval[-1].start_point - self.evaluator.eval[0].start_point)
            neck_length = effect_length - anchor_slack

            # Get thread's length : 80% of maximum
            thread_maxlength = abs(self.evaluator.eval[-1].end_point - self.evaluator.eval[-1].start_point)
            thread_length = thread_maxlength * 0.8

            # Create screw
            screw = WoodScrew(
                neck_length=neck_length,
                length=neck_length + thread_length,
            )

            return {
                'anchor': anchor,
                'screw': screw,
            }

        def get_constraints(self):
            last_part = self.evaluator.eval[-1].part
            return [
                Coincident(
                    self.components['screw'].mate_threadstart,
                    Mate(last_part, self.evaluator.eval[-1].start_coordsys - last_part.world_coords),
                ),
                Coincident(
                    self.components['anchor'].mate_screwhead,
                    self.components['screw'].mate_origin,
                ),
            ]

    class Applicator(Applicator):
        def apply_alterations(self):
            screw = self.selector.components['screw']
            anchor = self.selector.components['anchor']
            screw_cutter = screw.make_cutter()  # cutter in local coords
            anchor_cutter = anchor.make_cutter()

            # screw : cut from all effected parts
            for effect in self.evaluator.eval:
                screw_coordsys = screw.world_coords - effect.part.world_coords
                effect.part.local_obj = effect.part.local_obj.cut(screw_coordsys + screw_cutter)

            # anchor : all but last piece
            for effect in self.evaluator.eval[:-1]:
                anchor_coordsys = anchor.world_coords - effect.part.world_coords
                effect.part.local_obj = effect.part.local_obj.cut(anchor_coordsys + anchor_cutter)




# ------------------- Joined Planks -------------------

class ConnectedPlanks(cqparts.Assembly):
    fastener_class = EasyInstallFastener

    def make_components(self):
        # Wood panels
        p1 = WoodPanel(
            length=40, width=30,
            _render={'alpha': 0.5}
        )
        p2 = WoodPanel(
            length=40, width=30,
            _render={'alpha': 0.5}
        )

        # Fastener
        fastener = self.fastener_class(parts=[p1, p2])

        return {
            'panel1': p1,
            'panel2': p2,
            'fastener': fastener,
        }

    def make_constraints(self):
        # Pull out component references
        p1 = self.components['panel1']
        p2 = self.components['panel2']
        fastener = self.components['fastener']

        return [
            # Assembly's origin on panel1
            Fixed(p1.mate_origin),
            # Join panel at the corner
            Coincident(
                p2.mate_end,
                p1.get_mate_edge(p2.thickness),
            ),
            # Fastener assembly in the middle of a
            Coincident(
                fastener.mate_origin,  # mate_origin's -Z axis is used for evaluation
                p2.mate_end + CoordSystem(
                    origin=(0, 0, 25),  # 25mm above panel1 surface
                    xDir=(0, -1, 0)  # rotate so anchor faces inside
                ),
            ),
        ]

# ------------------- Catalogue -------------------

from cqparts.catalogue import JSONCatalogue
import tempfile

# Temporary catalogue (just for this script)
catalogue_filename = tempfile.mkstemp()[1]
#catalogue_filename = '/tmp/db.json'
catalogue = JSONCatalogue(catalogue_filename)

# Add screws to catalogue
#   note: this is the kind of information you'd store in a csv
#   file, then import with a script similar to this one, to convert that
#   information to a Catalogue.
screws = [
    {
        'id': 'screw_30',
        'obj_params': {  # parameters to WoodScrew constructor
            'neck_exposed': 5,
            'length': 40,  # exposing 10mm of thread
            'neck_length': 30,
        },
        'criteria': {
            'type': 'screw',
            'thread_length': 10,
            'compatible_anchor': 'anchor_10',
        },
    },
    {
        'id': 'screw_50',
        'obj_params': {
            'neck_exposed': 6,
            'length': 65,  # exposing 15mm of thread
            'neck_length': 50,

        },
        'criteria': {
            'type': 'screw',
            'thread_length': 15,
            'compatible_anchor': 'anchor_15',
        },
    },
]
for screw in screws:
    obj = WoodScrew(**screw['obj_params'])
    catalogue.add(id=screw['id'], criteria=screw['criteria'], obj=obj)


# Add anchors to catalogue
anchors = [
    {
        'id': 'anchor_10',
        'obj_params': {  # parameters to WoodScrew constructor
            'diameter': 10,
            'height': 7,
        },
        'criteria': {'type': 'anchor'},
    },
    {
        'id': 'anchor_15',
        'obj_params': {  # parameters to WoodScrew constructor
            'diameter': 15,
            'height': 10,
        },
        'criteria': {'type': 'anchor'},
    },
]
for anchor in anchors:
    obj = Anchor(**anchor['obj_params'])
    catalogue.add(id=anchor['id'], criteria=anchor['criteria'], obj=obj)


catalogue.close()


# ------------------- Catalogue : Fastener -------------------

from cqparts.catalogue import JSONCatalogue
from cqparts.utils import property_buffered

class EasyInstallCatalogueFastener(EasyInstallFastener):

    class Selector(EasyInstallFastener.Selector):

        def get_components(self):
            # Find minimum neck length (total effect length, minus last effect)
            neck_length_min = abs(self.evaluator.eval[-1].start_point - self.evaluator.eval[0].start_point)
            thread_length_max = abs(self.evaluator.eval[-1].end_point - self.evaluator.eval[-1].start_point)

            # Get the catalogue of available items
            catalogue = JSONCatalogue(catalogue_filename)
            item = catalogue.get_query()

            # Find viably sized wood-screw
            screw_item = sorted(
                catalogue.search(
                    # eval sets minimum evaluation length
                    (item.obj.params.neck_length >= neck_length_min) &
                    # thread shouldn't pierce through last part
                    (item.criteria.thread_length < thread_length_max)
                ),
                # sort by shortest first
                key=lambda x: x['obj']['params']['neck_length']
            )[0]  # first result; shortest screw

            return {
                'screw': catalogue.deserialize_result(screw_item),
                'anchor': catalogue.get(
                    item.id == screw_item['criteria']['compatible_anchor']
                ),
            }


class ConnectedPlanksCatalogue(ConnectedPlanks):
    fastener_class = EasyInstallCatalogueFastener



# ------------------- Export / Display -------------------
from cqparts.utils.env import env_name

# ------- Models
screw = WoodScrew()
anchor = Anchor()
panel = WoodPanel()

connected_exact = ConnectedPlanks()
connected_catalogue = ConnectedPlanksCatalogue()

if env_name == 'cmdline':
    screw.exporter('gltf')('screw.gltf')
    anchor.exporter('gltf')('anchor.gltf')
    panel.exporter('gltf')('panel.gltf')

    connected_exact.exporter('gltf')('connected_exact.gltf')
    print(connected_exact.tree_str(name='connected'))

    display(connected_exact)

elif env_name == 'freecad':
    pass  # manually switchable for testing
    #display(screw)
    #display(screw.make_cutter())
    #display(anchor)
    #display(together)

    display(connected_exact)


# ------------------- Catalogue : Cleanup -------------------

# Cleanup catalogue file (just for this script)
import os
os.unlink(catalogue_filename)
#print('catalogue: %s' % catalogue_filename)
