import os
import sys
import inspect
from math import (
    sin, cos, tan,
    radians,
)

if 'MYSCRIPT_DIR' in os.environ:
    _this_path = os.environ['MYSCRIPT_DIR']
else:
    _this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.insert(0, os.path.join(_this_path, '..', '..', 'src'))
#cadquery_path = os.path.join(_this_path, '..', '..', '..', 'cadquery')
#if os.path.exists(cadquery_path):
#    sys.path.insert(0, cadquery_path)

import cadquery
from Helpers import show

import cqparts
from cqparts.params import *
from cqparts.constraints.mate import Mate
from cqparts.constraints.lock import LockConstraint, RelativeLockConstraint

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


class Branch(cqparts.Part):
    """
    cylindrical branch to between
    """
    diameter = PositiveFloat(5, doc="diameter of cylinder")
    height = PositiveFloat(20, doc="cylinder's height")
    twist = Float(0, doc="twist angle of mount (degrees)")

    def make(self):
        return cadquery.Workplane("XY") \
            .circle(self.diameter / 2) \
            .extrude(self.height)

    @property
    def mate_top(self):
        # Mate point at the top of the cylinder, twist applied
        return Mate.from_plane(
            self.local_obj.faces(">Z").workplane().plane.rotated((0, 0, self.twist))
        )


class Splitter(cqparts.Part):
    """
    A house-shaped thingy to attach more branches to
    """
    width = PositiveFloat(10, doc="base width")
    height = PositiveFloat(12, doc="total height")
    angle_left = PositiveFloat(30, doc="angle of roof left (degrees)")
    angle_right = PositiveFloat(30, doc="angle of roof right (degrees)")

    _render = render_props(template='red')

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
        return Mate(
            origin=(-self.width / 4, 0, (self.height + self.left_wall_height) / 2),
            xDir=(0,1,0),
            normal=(-sin(radians(self.angle_left)), 0, cos(radians(self.angle_left)))
        )

    @property
    def mate_right(self):
        """Mate point in the center of the angled face on the right"""
        # TODO: query self.local_obj geometry to get center of face?
        return Mate(
            origin=(self.width / 4, 0, (self.height + self.right_wall_height) / 2),
            xDir=(0,1,0),
            normal=(sin(radians(self.angle_right)), 0, cos(radians(self.angle_right)))
        )


class BlockTree(cqparts.Assembly):
    trunk_diam = PositiveFloat(10, doc="trunk diameter")

    def make_components(self):
        cmp = {}
        # trunk
        cmp['trunk'] = Branch(diameter=self.trunk_diam)
        cmp['trunk_split'] = Splitter(angle_left=45)

        # branch L
        #cmp['branch_lb'] = Branch(diameter=4)
        #cmp['branch_ls'] = Splitter(angle_right=45)

        # branch R
        #cmp['branch_lb'] = Branch(diameter=2, height=)

        return cmp

    def make_constraints(self):
        cons = []

        # trunk
        cons.append(LockConstraint(
            self.components['trunk'],  # lock this
            mate=Mate((0,0,0), (1,0,0), (0,0,1)),  # here
        ))
        cons.append(RelativeLockConstraint(
            self.components['trunk_split'],  # lock this
            mate=components['trunk'].mate_top,  # here
            relataive_to=self.components['trunk'],  # relative to this
        ))

        # branch L
        # TODO

        # branch R
        # TODO

        return cons


house = Splitter()
display(house)

block_tree = BlockTree()
