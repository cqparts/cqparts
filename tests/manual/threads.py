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
from cqparts.solidtypes.threads import *
from cqparts.display import display, render_props

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
    for cls in cqparts.solidtypes.threads.search()
]
names_list = set()
for name_set in name_sets:
    names_list |= name_set
names_list = sorted(names_list)


from cqparts.utils.env import env_name
if (not args.name) and (env_name == 'freecad'):
    args.name = 'triangular'

if not args.name or args.list:
    # List screw drives and exit
    for name in names_list:
        print("  - %s" % name)

else:
    thread = find(name=args.name)()
    thread._simple = False  # force complex threads

    if env_name == 'freecad':
        # force complex thread
        from Helpers import show
        show(thread.obj)
        show(thread.profile)

    else:
        display(thread)
