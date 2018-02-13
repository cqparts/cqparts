#!/usr/bin/env python

import argparse
import sys
import itertools

import cqparts
from cqparts.catalogue import JSONCatalogue


# Threads
from cqparts_fasteners.solidtypes import threads


# Commandline arguments
parser = argparse.ArgumentParser(description="Generate a test catalogue")

parser.add_argument(
    'out', type=str, nargs='?',
    default='thread_catalogue.json',
    help='filename to output'
)

args = parser.parse_args()


catalogue = JSONCatalogue(args.out, clean=True)


# -------- Add catalogue items

names = ['ball_screw', 'iso68', 'triangular']
lengths = [1, 2, 4, 10]
diameters = [1, 3, 4, 5]

for (i, (name, length, diam)) in enumerate(itertools.product(names, lengths, diameters)):
    thread = threads.find(name=name)(
        _simple=False, length=length, diameter=diam,
    )
    print("adding: %r" % thread)
    catalogue.add(
        "%s_%gx%g_%03i" % (name, length, diam, i),
        thread,
        criteria={
            'type': name, 'length': length, 'diam': diam,
        },
    )


# close catalogue after additions
catalogue.close()
