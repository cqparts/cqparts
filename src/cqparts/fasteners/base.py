import six
from math import tan
from math import radians

import cadquery

from ..part import Assembly
from ..params import *
from .utils import Evaluator, Selector, Applicator

import logging
log = logging.getLogger(__name__)



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
