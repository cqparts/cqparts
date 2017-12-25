
from ..params import *

from .male import MaleFastenerPart
from .base import Fastener
from .params import HeadType, DriveType, ThreadType
from .utils import VectorEvaluator, Selector, Applicator
from ..solidtypes import threads
from ..constraint import Mate, Coincident
from ..utils import CoordSystem

import logging
log = logging.getLogger(__name__)


class Screw(MaleFastenerPart):
    """
    Part representing a single screw
    """

    head = HeadType(
        default=('countersunk', {
            'diameter': 9.5,
            'height': 3.5,
        }),
        doc="head type and parameters"
    )
    drive = DriveType(
        default=('phillips', {
            'diameter': 5.5,
            'depth': 2.5,
            'width': 1.15,
        }),
        doc="screw drive type and parameters"
    )
    thread = ThreadType(
        default=('triangular', {
            'diameter': 5,
            'pitch': 2,
            'angle': 20,
        }),
        doc="thread type and parameters",
    )
    neck_taper = FloatRange(0, 90, 15, doc="angle of neck's taper (0 is parallel with neck)")
    neck_length = PositiveFloat(7.5, doc="length of neck")
    length = PositiveFloat(25, doc="screw's length")
    tip_length = PositiveFloat(5, doc="length of taper on a pointed tip")


class ScrewFastener(Fastener):
    Evaluator = VectorEvaluator

    class Selector(Selector):
        ratio = 0.8
        def get_components(self):
            end_effect = self.evaluator.eval[-1]
            end_point = end_effect.start_point + (end_effect.end_point - end_effect.start_point) * self.ratio

            return {'screw': Screw(
                head=('countersunk', {
                    'diameter': 9.5,
                    'height': 3.5,
                }),
                neck_length=abs(self.evaluator.eval[-1].start_point - self.evaluator.eval[0].start_point),
                # only the length after the neck is threaded
                length=abs(end_point - self.evaluator.eval[0].start_point),
                #length=abs(self.evaluator.eval[-1].end_point - self.evaluator.eval[0].start_point),
            )}

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            anchor_part = self.evaluator.eval[-1].part  # last effected part

            return [Coincident(
                self.components['screw'].mate_origin,
                Mate(anchor_part, self.evaluator.eval[0].start_coordsys - anchor_part.world_coords)
            )]

    class Applicator(Applicator):

        def apply_alterations(self):
            screw = self.selector.components['screw']
            cutter = screw.make_cutter()  # cutter in local coords

            for effect in self.evaluator.eval:
                relative_coordsys = screw.world_coords - effect.part.world_coords
                local_cutter = relative_coordsys + cutter
                effect.part.local_obj = effect.part.local_obj.cut(local_cutter)
