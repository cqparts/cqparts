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
from cqparts.solidtypes.screw_drives import *
from cqparts.display import display, render_props

from cqparts.utils.env import env_name

import logging
log = logging.getLogger(__name__)


# ---- create commandline parser
parser = argparse.ArgumentParser(description='Display screw drives.')

parser.add_argument('-l', '--list',
                    action='store_const', const=True, default=False,
                    help="list possible screw drive names")
parser.add_argument('name', nargs='?',
                    help="name of screw drive")
parser.add_argument('-a', '--alpha', type=float, default=0.5 if env_name == 'freecad' else 1.0,
                    help="alpha of each part")

args = parser.parse_args()


# Get list of names
name_sets = [
    cqparts.search.class_criteria[cls].get('name', set())
    for cls in cqparts.solidtypes.screw_drives.search()
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


class ScrewDriveParam(Parameter):
    """
    Screw drive parameter, finds a screw drive type based its name.
    """
    def type(self, value):
        if isinstance(value, str):
            return cqparts.solidtypes.screw_drives.find(name=value)()
        raise ValueError()

class ScrewDriveBox(cqparts.Part):
    """
    A box with a screw drive indentation cut out of the top face.
    """
    drive = ScrewDriveParam(None)
    size = PositiveFloat(5)
    height = PositiveFloat(5)

    _render = render_props(alpha=args.alpha)

    def make(self):
        box = cadquery.Workplane('XY').rect(self.size, self.size) \
            .extrude(-self.height)
        box = self.drive.apply(box)
        return box

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
    Collection of screw drive boxes, layed out in a square pattern
    """
    names = NamesParam()
    box_size = PositiveFloat(5)
    box_height = PositiveFloat(5)
    gap = PositiveFloat(2)

    def make_components(self):
        components = {}
        for name in self.names:
            components[name] = ScrewDriveBox(
                drive=name,
                size=self.box_size,
                height=self.box_height,
            )
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
