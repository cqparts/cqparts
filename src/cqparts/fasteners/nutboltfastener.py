from .base import Fastener
from .utils import VectorEvaluator, Selector, Applicator
from ..constraint import Mate, Coincident

from .nuts import HexNut
from .bolts import HexBolt

class NutAndBoltFastener(Fastener):
    Evaluator = VectorEvaluator

    class Selector(Selector):
        def get_components(self):
            effect_length = abs(self.evaluation.eval[-1].end_point - self.evaluation.eval[0].start_point)

            nut = HexNut()
            bolt = HexBolt(
                length=effect_length + nut.height,
            )

            return {
                'bolt': bolt,
                'nut': nut,
            }

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            first_part = self.evaluation.eval[0].part
            last_part = self.evaluation.eval[-1].part  # last effected part

            return [
                Coincident(
                    self.components['bolt'].mate_origin,
                    Mate(first_part, self.evaluation.eval[0].start_coordsys - first_part.world_coords)
                ),
                Coincident(
                    self.components['nut'].mate_origin,
                    Mate(last_part, self.evaluation.eval[-1].end_coordsys - last_part.world_coords)
                ),
            ]

    class Applicator(Applicator):
        def apply(self):
            bolt = self.selector.components['bolt']
            cutter = bolt.make_cutter()  # cutter in local coords

            for effect in self.evaluation.eval:
                relative_coordsys = bolt.world_coords - effect.part.world_coords
                local_cutter = relative_coordsys + cutter
                effect.part.local_obj = effect.part.local_obj.cut(local_cutter)
