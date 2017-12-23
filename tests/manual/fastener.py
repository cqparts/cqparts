#!/usr/bin/env python

import os
import sys
import inspect
import logging

import cadquery
import cqparts

from cqparts.params import *
from cqparts.basic.primatives import Box
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.display import display
from cqparts.utils.geometry import CoordSystem

from cqparts.fasteners.utils import VectorEvaluator
#from cqparts.fasteners import Fastener
from cqparts.fasteners.screws import ScrewFastener

from cqparts.fasteners.nutboltfastener import NutAndBoltFastener


# enable logging
cadquery.freecad_impl.console_logging.enable(logging.INFO)
log = logging.getLogger(__name__)

alpha = 0.5

class Thing(cqparts.Assembly):
    def make_components(self):
        anchor = Box(length=15, width=20, height=15, _render={'alpha':alpha})
        plate = Box(length=25, width=15, height=7, _render={'alpha':alpha})
        return {
            'anchor': anchor,
            'plate': plate,
            'fastener': NutAndBoltFastener(parts=[plate, anchor]),
            #'fastener': ScrewFastener(parts=[plate, anchor]),
        }

    def make_constraints(self):
        return [
            Fixed(
                self.components['anchor'].mate_origin,
            ),
            Coincident(
                self.components['plate'].mate_origin,
                self.components['anchor'].mate_top,
            ),
            Coincident(
                self.components['fastener'].mate_origin,
                self.components['plate'].mate_top,
            ),
        ]


# ------------------- Export / Display -------------------
from cqparts.utils.env import get_env_name

env_name = get_env_name()

# ------- Models
thing = Thing()
thing.world_coords = CoordSystem()
#thing.world_coords = CoordSystem(origin=(1, 2, 3), xDir=(0,1,-1), normal=(1,0.3,0))

log.info(thing.tree_str(name="thing", prefix='    '))

if env_name == 'cmdline':
    display(thing)

elif env_name == 'freecad':
    display(thing)
