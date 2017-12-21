#!/usr/bin/env python

import os
import sys
import inspect

if 'MYSCRIPT_DIR' in os.environ:
    _this_path = os.environ['MYSCRIPT_DIR']
else:
    _this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'src'))
#cadquery_path = os.path.join(_this_path, '..', '..', '..', 'cadquery')
#if os.path.exists(cadquery_path):
#    sys.path.insert(0, cadquery_path)

from math import (
    sin, cos, tan,
    radians,
)

import cadquery
from Helpers import show

import logging
try:
    cadquery.freecad_impl.console_logging.enable(logging.INFO)
except AttributeError:
    pass  # outdated cadquery, no worries

log = logging.getLogger()
#log.info("----------------- Block Tree ----------------")

import cqparts
from cqparts.params import *
from cqparts.constraint import Mate
from cqparts.constraint import Fixed, Coincident
from cqparts.utils.geometry import CoordSystem

from cqparts.display import display, render_props


# Block Tree?
#
#   This is a simple concept intended to test mating parts.
#   There are 2 types of part:
#       - a branch; cylinder
#       - a splitter; "house" shaped block (a rectangle with a triangle on top)
#                like this:    /\
#                             /  \
#                            |    |
#                            |____|
#
#   Mates are positioned in the Part instances, which are used by the Assembly.
#   These building blocks are used to create a sort of wooden "tree".


# ------------------- Parts --------------------
class Branch(cqparts.Part):
    """
    cylindrical branch to between
    """
    diameter = PositiveFloat(5, doc="diameter of cylinder")
    height = PositiveFloat(10, doc="cylinder's height")
    twist = Float(0, doc="twist angle of mount (degrees)")

    _render = render_props(template='glass')

    def make(self):
        return cadquery.Workplane("XY") \
            .circle(self.diameter / 2) \
            .extrude(self.height)

    @property
    def mate_top(self):
        # Mate point at the top of the cylinder, twist applied
        return Mate(self, CoordSystem.from_plane(
            self.local_obj.faces(">Z").workplane().plane.rotated((0, 0, self.twist))
        ))


class Splitter(cqparts.Part):
    """
    A house-shaped thingy to attach more branches to
    """
    width = PositiveFloat(10, doc="base width")
    height = PositiveFloat(12, doc="total height")
    angle_left = PositiveFloat(30, doc="angle of roof left (degrees)")
    angle_right = PositiveFloat(30, doc="angle of roof right (degrees)")

    _render = render_props(template='glass')

    def __init__(self, *args, **kwargs):
        super(Splitter, self).__init__(*args, **kwargs)
        # Calculate wall heights, they're used for construction, and mates
        self.left_wall_height = self.height - ((self.width / 2) * tan(radians(self.angle_left)))
        self.right_wall_height = self.height - ((self.width / 2) * tan(radians(self.angle_right)))
        assert self.left_wall_height > 0, "bad left angle"
        assert self.right_wall_height > 0, "bad right angle"

    def make(self):
        points = [
            # base
            (-self.width / 2, 0), (self.width / 2, 0),
            # roof
            (self.width / 2, self.right_wall_height),
            (0, self.height),
            (-self.width / 2, self.left_wall_height),
        ]
        obj = cadquery.Workplane("XZ", origin=(0, self.width / 2, 0)) \
            .move(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)
        return obj

    @property
    def mate_left(self):
        """Mate point in the center of the angled face on the left"""
        # TODO: query self.local_obj geometry to get center of face?
        return Mate(self, CoordSystem(
            origin=(-self.width / 4, 0, (self.height + self.left_wall_height) / 2),
            xDir=(0,1,0),
            normal=(-sin(radians(self.angle_left)), 0, cos(radians(self.angle_left)))
        ))

    @property
    def mate_right(self):
        """Mate point in the center of the angled face on the right"""
        # TODO: query self.local_obj geometry to get center of face?
        return Mate(self, CoordSystem(
            origin=(self.width / 4, 0, (self.height + self.right_wall_height) / 2),
            xDir=(0,1,0),
            normal=(sin(radians(self.angle_right)), 0, cos(radians(self.angle_right)))
        ))


# ------------------- Tree --------------------
#   note: each assembly has parts all the same colour to (show grouping).
#
#   Tree's hierarchy:
#      [red]    trunk + left branch are all in a single assembly
#      [green]  right branch (Branch + Splitter + 2 branches)
#      [blue]   little blue house (with a chimney)
#      [yellow] left right branch (Branch)
#
#   This example is not demonstrating good design, it's just to illustrate
#   different ways of grouping, and to make sure everything aligns.
#

class BlueHouse(cqparts.Assembly):
    roof_angle = PositiveFloat(10, doc="chimney angle for chimney roof bit")
    house_size = PositiveFloat(7, doc="square size of little house")

    def make_components(self):
        blue = {'color': (0,0,255), 'alpha': 0.5}
        return {
            'foo': Splitter(
                width=self.house_size,
                height=self.house_size,
                angle_right=self.roof_angle,
                _render=blue
            ),
            'bar': Branch(diameter=3, height=2, _render=blue),
        }

    def make_constraints(self):
        return [
            Fixed(
                self.components['foo'].mate_origin,  # lock to origin
            ),
            Coincident(
                self.components['bar'].mate_origin, # lock this
                self.components['foo'].mate_right,  # to this
            ),
        ]


class GreenBranch(cqparts.Assembly):
    def make_components(self):
        green = {'color': (0,255,0), 'alpha': 0.5}
        return {
            'branch': Branch(height=3, _render=green),
            'split': Splitter(_render=green),
            'L': Branch(_render=green),
            'R': Branch(_render=green),
            'house': BlueHouse(),
        }

    def make_constraints(self):
        return [
            Fixed(
                self.components['branch'].mate_origin,  # lock this
                CoordSystem((0,0,0), (1,0,0), (0,0,1)),  # here
            ),
            Coincident(
                self.components['split'].mate_origin,  # lock this
                self.components['branch'].mate_top,  # here
            ),
            Coincident(
                self.components['L'].mate_origin,  # lock this
                self.components['split'].mate_left,  # here
            ),
            Coincident(
                self.components['R'].mate_origin,  # lock this
                self.components['split'].mate_right,  # here
            ),
            Coincident(
                self.components['house'].mate_origin,  # lock this
                self.components['R'].mate_top,  # here
            ),
        ]


class BlockTree(cqparts.Assembly):
    trunk_diam = PositiveFloat(10, doc="trunk diameter")

    def make_components(self):
        red = {'color': (255,0,0), 'alpha': 0.9}
        components = {
            'trunk': Branch(diameter=self.trunk_diam, twist=20, _render=red),
            'trunk_split': Splitter(angle_left=60, _render=red),
            'branch_lb': Branch(diameter=4, _render=red),
            'branch_ls': Splitter(angle_right=30, _render=red),
            'branch_r': GreenBranch(),
        }

        # branch R
        #cmp['branch_lb'] = Branch(diameter=2, height=)

        return components

    def make_constraints(self):
        return [
            # trunk
            Fixed(
                self.components['trunk'].mate_origin,  # lock this
                CoordSystem((0,0,0), (1,0,0), (0,0,1)),  # here
            ),
            Coincident(
                self.components['trunk_split'].mate_origin,  # lock this
                self.components['trunk'].mate_top,  # here
            ),

            # branch L
            Coincident(
                self.components['branch_lb'].mate_origin,
                self.components['trunk_split'].mate_left,
            ),
            Coincident(
                self.components['branch_ls'].mate_origin,
                self.components['branch_lb'].mate_top,
            ),

            # branch RL
            Coincident(
                self.components['branch_r'].mate_origin,
                self.components['trunk_split'].mate_right,
            ),
        ]


#house = Splitter()
#display(house)

#block_tree.world_coords = CoordSystem()

# ------------------- Export / Display -------------------
from cqparts.utils.env import get_env_name

env_name = get_env_name()

# ------- Models
block_tree = BlockTree(trunk_diam=7)

#import ipdb
#ipdb.set_trace()

if env_name == 'cmdline':
    block_tree.exporter('gltf')('exports/block-tree.gltf', embed=True)
    print(block_tree.tree_str(name="block_tree"))

elif env_name == 'freecad':
    pass  # manually switchable for testing
    display(block_tree)
