#!/usr/bin/env python

import os
import sys
import math
import argparse

import cadquery
import cqparts
from cqparts.params import *
from cqparts.constraint import *
from cqparts.utils import CoordSystem
from cqparts.display import display, render_props

import cqparts_fasteners
from cqparts_fasteners.solidtypes.fastener_heads import *

import logging
log = logging.getLogger(__name__)


# ---- create commandline parser
parser = argparse.ArgumentParser(description='Display fastener heads.')

parser.add_argument('-l', '--list',
                    action='store_const', const=True, default=False,
                    help="list possible screw drive names")
parser.add_argument('name', nargs='?',
                    help="name of screw drive")
parser.add_argument('-a', '--alpha', type=float, default=0.5,
                    help="alpha of each part")

args = parser.parse_args()

# Get list of names
name_sets = [
    cqparts.search.class_criteria[cls].get('name', set())
    for cls in cqparts_fasteners.solidtypes.fastener_heads.search()
]
names_list = set()
for name_set in name_sets:
    names_list |= name_set
names_list = sorted(names_list)


if args.list:
    # List screw drives and exit
    for name in names_list:
        print("  - %s" % name)

    exit(0)


class NamesParam(Parameter):
    """
    List of screw-drive names
    """
    def type(self, value):
        if isinstance(value, (list, tuple)):
            return value
        raise ValueError()

class Showcase(cqparts.Assembly):
    """
    Collection of screw drive boxes, laid out in a square pattern
    """
    names = NamesParam()
    box_size = PositiveFloat(5)
    box_height = PositiveFloat(5)
    gap = PositiveFloat(2)

    def make_components(self):
        components = {}
        for name in self.names:
            cls = cqparts_fasteners.solidtypes.fastener_heads.find(name=name)
            components[name] = cls(_render={'alpha': 0.5})
        return components

    def make_constraints(self):
        constraints = []
        index_width = int(math.sqrt(len(self.names)))
        for (i, name) in enumerate(self.names):
            (row, col) = ((i % index_width), int(i / index_width))

            constraints.append(Fixed(
                self.components[name].mate_origin,
                CoordSystem(origin=(
                    row * (self.box_size + self.gap),
                    -col * (self.box_size + self.gap),
                    0
                )),
            ))

        return constraints


names = names_list
if args.name:
    # single
    names = [args.name]

showcase = Showcase(names=names)

display(showcase)
