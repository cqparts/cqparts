#!/usr/bin/env python

import os
import sys
import inspect
import logging

import cadquery
import cqparts

from cqparts.params import *
from cqparts_misc.basic.primatives import Box
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.display import display
from cqparts.utils.geometry import CoordSystem

from cqparts_fasteners.utils import VectorEvaluator
#from cqparts_fasteners import Fastener

from cqparts_fasteners.fasteners.screw import ScrewFastener
from cqparts_fasteners.fasteners.nutbolt import NutAndBoltFastener


# enable logging
cadquery.freecad_impl.console_logging.enable(logging.INFO)
log = logging.getLogger(__name__)

alpha = 0.5

class Thing(cqparts.Assembly):
    def make_components(self):
        anchor = Box(length=25, width=30, height=15, _render={'alpha':alpha})
        plate = Box(length=35, width=25, height=9, _render={'alpha':alpha})
        return {
            'anchor': anchor,
            'plate': plate,
            #'fastener': NutAndBoltFastener(parts=[plate, anchor]),
            'fastener': ScrewFastener(parts=[plate, anchor]),
        }

    def make_constraints(self):
        anchor = self.components['anchor']
        plate = self.components['plate']
        fastener = self.components['fastener']
        return [
            Fixed(anchor.mate_origin),
            Coincident(plate.mate_origin, anchor.mate_top),
            Coincident(fastener.mate_origin, plate.mate_top),
        ]


# ------------------- Export / Display -------------------
from cqparts.utils.env import env_name

# ------- Models
thing = Thing()
thing.world_coords = CoordSystem()
#thing.world_coords = CoordSystem(origin=(1, 2, 3), xDir=(0,1,-1), normal=(1,0.3,0))
#thing.world_coords = CoordSystem.random()

log.info(thing.tree_str(name="thing", prefix='    '))

if env_name == 'cmdline':
    display(thing)

elif env_name == 'freecad':
    display(thing)
