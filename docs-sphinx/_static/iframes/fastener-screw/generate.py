#!/usr/bin/env python

# The code here should be representative of that in:
#   https://cqparts.github.io/cqparts/doc/tutorials/assembly.html


# ------------------- Thing -------------------

import cqparts
from cqparts.constraint import Fixed, Coincident
from cqparts_fasteners.fasteners.screw import ScrewFastener
from cqparts_misc.basic.primatives import Box

from cqparts.utils import CoordSystem

class Thing(cqparts.Assembly):
    def make_components(self):
        base = Box(length=20, width=30, height=15)
        top = Box(length=40, width=20, height=5)
        return {
            'base': base,
            'top': top,
            'fastener': ScrewFastener(parts=[base, top]),
        }

    def make_constraints(self):
        base = self.components['base']
        top = self.components['top']
        fastener = self.components['fastener']
        return [
            Fixed(base.mate_bottom),
            Coincident(top.mate_bottom, base.mate_top),
            Coincident(fastener.mate_origin, top.mate_top),
        ]

thing = Thing()


# ------------------- Export -------------------

from cqparts.params import *
from cqparts.display import display
from cqparts.display import get_display_environment
env_name = get_display_environment().name

if env_name == 'freecad':
    display(thing)
else:
    thing.exporter('gltf')('thing.gltf', embed=False)
