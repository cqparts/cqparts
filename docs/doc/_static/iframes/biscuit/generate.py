#!/usr/bin/env python

# ------------------- Wood Panel -------------------

from math import radians, tan, cos
import cadquery

import cqparts
from cqparts.params import *
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem

from cqparts.display import display, render_props


class Panel(cqparts.Part):
    # dimensions
    height = PositiveFloat(50, doc="panel height (along join)")
    depth = PositiveFloat(50, doc="panel depth (from join to opposite side)")
    width = PositiveFloat(10, doc="thickness of panel")
    join_angle = FloatRange(0, 89, 45, doc="angle of join (unit: degrees)")

    _render = render_props(template='wood', alpha=0.5)

    def make(self):

        points = [
            (0, 0),
            (self.depth, 0),
            (self.depth, self.width),
            (self.width * tan(radians(self.join_angle)), self.width),
        ]
        return cadquery.Workplane('XZ', origin=(0, self.height / 2, 0)) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.height)

    def get_mate_join(self, ratio=0.5):
        # Return a mate that's somewhere along the join surface.
        return Mate(self, (
            CoordSystem().rotated(
                (0, -(90 - self.join_angle), 0)
            ) + CoordSystem(
                origin=(
                    (self.width / cos(radians(self.join_angle))) / 2,
                    (-self.height / 2) + (self.height * ratio),
                    0
                ),
            )
        ))

    @property
    def mate_join(self):
        # default is half way along join
        return self.get_mate_join(ratio=0.5)

    @property
    def mate_join_reverse(self):
        # reversed join rotated around X-axis 180 deg
        return self.mate_join + CoordSystem().rotated((180, 0, 0))


# ------------------- Biscuit -------------------

class Biscuit(cqparts.Part):
    # Biscuit Dimensions
    width = PositiveFloat(30, doc="twice penetration depth")
    length = PositiveFloat(None, doc="length tip to tip")
    thickness = PositiveFloat(5, doc="material thickness")

    _render = render_props(template='wood_dark')

    def initialize_parameters(self):
        super(Biscuit, self).initialize_parameters()
        # set default length as a ratio of width
        if self.length is None:
            self.length = (5. / 3) * self.width

    def make(self):
        # We'll just use the simplified model for this example
        return self.make_simple()
        # It could be rounded at the ends, and the sides chamfered, but
        # for this example we'll just keep it simple.

    def make_simple(self):
        # Biscuit shaped like a eye, 2 arcs from end to end (length)
        # Create left & right side, union them together
        biscuit = cadquery.Workplane('XY')
        for i in [1, -1]:
            biscuit = biscuit.union(
                cadquery.Workplane('XY', origin=(0, 0, -self.thickness / 2)) \
                    .moveTo(self.length / 2, 0) \
                    .threePointArc(
                        (0, i * self.width / 2),
                        (-self.length / 2, 0)
                    ).close().extrude(self.thickness)
            )

        return biscuit

    def make_cutter(self):
        # the cutaway material is the same shape as the biscuit itself
        # (the simplified model)
        return self.make_simple()


# ------------------- Biscuit Fastener -------------------

from cqparts_fasteners.fasteners.base import Fastener
from cqparts_fasteners.utils.evaluator import Evaluator, VectorEvaluator
from cqparts_fasteners.utils.selector import Selector
from cqparts_fasteners.utils.applicator import Applicator

from cqparts.constraint import Fixed
from itertools import chain


class BiscuitFastener(Fastener):
    # Parameters
    ratio = FloatRange(0, 1, 0.5, doc="ratio penetration of biscuit into parts")
    cut_biscuit_holes = Boolean(True, doc="if True, biscuit holes are cut into pannels")

    class Evaluator(Evaluator):
        # Bi-directional evaluator, employes 2 VectorEvaluator instances that,
        # on their own, evaluate in the -Z direction
        def __init__(self, parts, location, parent=None):
            super(BiscuitFastener.Evaluator, self).__init__(parts=parts, parent=parent)
            self.location = location
            # positive z direction
            self.eval_pos = VectorEvaluator(parts, location.rotated((180, 0, 0)))
            # negative z direction
            self.eval_neg = VectorEvaluator(parts, location)

        def perform_evaluation(self):
            return (self.eval_pos.eval, self.eval_neg.eval)

    class Selector(Selector):
        def get_components(self):
            # Determine maximum biscuit width from the evaluations
            (pos, neg) = self.evaluator.eval
            pos_length = abs(pos[-1].end_point - pos[0].start_point)
            neg_length = abs(neg[-1].end_point - neg[0].start_point)
            max_width = 2 * min(
                pos_length * self.parent.ratio,  # parent is the BiscuitFastener instance
                neg_length * self.parent.ratio
            )

            return {
                'biscuit': Biscuit(
                    width=max_width,
                    thickness=max_width * 0.1,
                ),
            }

        def get_constraints(self):
            #(pos, neg) = self.evaluator.eval
            return [
                Fixed(
                    self.components['biscuit'].mate_origin,
                    CoordSystem().rotated((90, 0, 90))  # corectly orientate biscuit
                ),
            ]

    class Applicator(Applicator):
        def apply_alterations(self):
            if not self.parent.cut_biscuit_holes:
                return  # fastener configured to place biscuit overlapping panel

            # Get the biscuit cutout shape
            biscuit = self.selector.components['biscuit']
            biscuit_cutter = biscuit.make_cutter()  # cutter in local coords

            # Duplicate parts possible with floating point rounding, because the
            # evaluator is placed on the 2 planar surfaces being joined.
            effected_parts = set([  # duplicates are removed within the set
                effect.part for effect in chain(*self.evaluator.eval[:])
            ])

            # Move biscuit relative to altered part's local coordinates, then
            # alter the part's obj.
            for part in effected_parts:
                biscuit_coordsys = biscuit.world_coords - part.world_coords
                part.obj = part.obj.cut(biscuit_coordsys + biscuit_cutter)


# ------------------- Corner Assembly -------------------

from cqparts.constraint import Fixed, Coincident


class CornerAssembly(cqparts.Assembly):
    biscuit_count = PositiveInt(2, doc="number of biscuits")
    join_angle = FloatRange(0, 89, 45, doc="angle of join (unit: degrees)")
    biscuit_holes = Boolean(True, doc="if True, holes are cut into pannels to house biscuits")

    def make_components(self):
        components = {
            'a': Panel(join_angle=self.join_angle),
            'b': Panel(join_angle=self.join_angle),
        }
        for i in range(self.biscuit_count):
            components['f_%i' % i] = BiscuitFastener(
                parts=[components['a'], components['b']],
                cut_biscuit_holes=self.biscuit_holes,
            )
        return components

    def make_constraints(self):
        # position joined panels
        a = self.components['a']
        b = self.components['b']
        yield [
            Fixed(a.mate_origin),
            Coincident(
                b.mate_join_reverse,
                a.mate_join
            ),
        ]

        # position biscuits along join
        biscuits = [
            c for c in self.components.values()
            if isinstance(c, BiscuitFastener)
        ]
        yield [
            Coincident(
                c.mate_origin,
                a.get_mate_join(
                    ratio=(i + 1) * (1. / (len(biscuits) + 1))
                )
            )
            for (i, c) in enumerate(biscuits)
        ]


# ------------------- Export / Display -------------------
from cqparts.display import display
from cqparts.display import get_display_environment
env_name = get_display_environment().name

# ------- Models
panel = Panel()
biscuit = Biscuit()
corner_assembly = CornerAssembly(
    join_angle=45,
    biscuit_holes=True,
)

if env_name == 'cmdline':
    panel.exporter('gltf')('panel.gltf')
    biscuit.exporter('gltf')('biscuit.gltf')
    corner_assembly.exporter('gltf')('corner_assembly.gltf')

    print(corner_assembly.tree_str())

    #display(panel)
    #display(biscuit)
    #display(corner_assembly)

elif env_name == 'freecad':
    #display(panel)
    #display(biscuit)
    display(corner_assembly)
