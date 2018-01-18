#!/usr/bin/env python

import argparse
import sys

import cqparts
from cqparts.catalogue import JSONCatalogue

sys.path.append('..')

import partslib


# Commandline arguments
parser = argparse.ArgumentParser(description="Generate a test catalogue")

parser.add_argument(
    'out', type=str, nargs='?',
    default='catalogue.json',
    help='filename to output'
)

args = parser.parse_args()


catalogue = JSONCatalogue(args.out, clean=True)

# -------- Add catalogue items

box_data = [
    ('box_a', {'length': 10, 'width': 10, 'height': 10}),
    ('box_b', {'length': 20, 'width': 20, 'height': 20}),
    ('box_c', {'length': 10, 'width': 20, 'height': 30}),
]
for (idstr, params) in box_data:
    obj = partslib.Box(**params)
    print("adding: %r" % obj)
    catalogue.add(id=idstr, obj=obj, criteria={})

cylinder_data = [
    ('cyl_a', {'length': 5, 'radius': 3}),
    ('cyl_b', {'length': 10, 'radius': 0.5}),
    ('cyl_c', {'length': 4, 'radius': 10}),
]
for (idstr, params) in cylinder_data:
    obj = partslib.Cylinder(**params)
    print("adding: %r" % obj)
    catalogue.add(id=idstr, obj=obj, criteria={})

cubestack_data = [
    ('cs_01', {'size_a': 2, 'size_b': 1}),
    ('cs_02', {'size_a': 10, 'size_b': 4}),
    ('cs_03', {'size_a': 1, 'size_b': 10}),
]
for (idstr, params) in cubestack_data:
    obj = partslib.CubeStack(**params)
    print("adding: %r" % obj)
    catalogue.add(id=idstr, obj=obj, criteria={})

simplecar_data = [
    ('ford', {'width': 50, 'length': 100, 'wheelbase': 50, 'wheel_radius': 10}),
    ('holden', {'width': 40, 'length': 90, 'wheelbase': 40, 'wheel_radius': 20}),
    ('merc', {'width': 60, 'length': 120, 'wheelbase': 90, 'wheel_radius': 25}),
]
for (idstr, params) in simplecar_data:
    obj = partslib.SimpleCar(**params)
    print("adding: %r" % obj)
    catalogue.add(id=idstr, obj=obj, criteria={})

# close catalogue after additions
catalogue.close()
