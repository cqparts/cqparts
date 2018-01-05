"""
Functional implementation of the tutorial in :ref:`tutorials_fastener-easy-install`
"""

import cadquery
import cqparts

# cqparts: parameters
from cqparts.params import PositiveFloat, Boolean

# cqparts: fasteners
from cqparts_fasteners import Fastener
from cqparts_fasteners.utils.evaluator import VectorEvaluator
from cqparts_fasteners.utils.selector import Selector
from cqparts_fasteners.utils.applicator import Applicator

# from cqparts_fasteners.params import HeadType, DriveType, ThreadType


# -------------------------- Parts --------------------------

class WoodScrew(cqparts.Part):
    diameter = PositiveFloat(default=3, doc="bore hole diameter")
    thread_length = PositiveFloat(default=5, doc="distance the screw bores into part")
    # TODO: more parameters

    def make(self):
        TODO: code for wood screw make()


class Anchor(cqparts.Part):
    diameter = PositiveFloat(default=10, doc="bore diameter for anchor")
    reversed = Boolean(default=False, doc="if True, screw drive is put on the reverse side")
    # TODO more parameters

    def make(self):
        # TODO: code to build anchor


# -------------------------- Fastener --------------------------

class EasyInstallEvaluator(VectorEvaluator):
    def __init__(self, parts, start, dir, anchor_plane):
        super(EasyInstallEvaluator, self).__init__(parts, start, dir)
        self.anchor_plane = anchor_plane

    @property
    def anchor_norm(self):
        return self.anchor_plane.zDir


class EasyInstallSelector(Selector):
    #TODO: code for selector
    # note: selector must return a wood-screw and anchor
    #       does it return a Fastener instance?
    pass

    def get_selection(self):
        # TODO: returns single Fastener instance
        # if there are multiple viable choices, it's up to the selector
        # to narrow it down to a single selection.
        pass


class EasyInstallApplicator(Applicator):
    # TODO: code for applicator
    pass


class EasyInstallFastener(Fastener):
    EVALUATOR_CLASS = EasyInstallEvaluator
    SELECTOR_CLASS = EasyInstallSelector
    APPLICATOR_CLASS = EasyInstallApplicator

    def make(self):
        screw = WoodScrew()  # TODO: parameters + mate

        anchor = Anchor()  # TODO: parameters + mate

        return {
            'wood_screw': screw,
            'anchor': anchor,
        }

# -------------------------- Using the Fastener --------------------------

import cadquery

class Panel1(cqparts.Part):
    def make(self):
        return cadquery.Workplane('XY', origin=(0, -50, -10)) \
            .box(100, 100, 10, centered=(False, False, False))

class Panel2(cqparts.Part):
    def make(self):
        return cadquery.Workplane('XY', origin=(0, -50, 0)) \
            .box(10, 100, 100, centered=(False, False, False))


# TODO: 2 instances of the same panel, different orientation
horizontal = Panel1()
vertical = Panel2()

# Find vertical panel's centre
#   note: the vertical panel is built horizontally, **then** rotated upright.
#         so we're finding the vector we want in it's local coordinates, then
#         we're converting them to word coordinates to perform the evaluation.
v_bot = vertical.local_obj.faces("<Z").workplane().plane
v_top = vertical.local_obj.faces(">Z").workplane().plane
midpoint = (v_bot.origin + v_top.origin).multiply(0.5)

# direction of bolt (normal to horizontal panel)



evaluation = EasyInstallFastener.evaluate(
    parts=[horizontal, vertical],
    start=mid,
    parts, start, dir, anchor_plane
