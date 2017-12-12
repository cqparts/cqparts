#!/usr/bin/env python

import sys
import os
import inspect

if 'MYSCRIPT_DIR' in os.environ:
    _this_path = os.environ['MYSCRIPT_DIR']
else:
    _this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', '..', '..', 'src'))

# -------------------------- Cylinder Part --------------------------

import cadquery
import cqparts
from cqparts.params import *
from cqparts.display import display, render_props
from cqparts.utils.geometry import CoordSystem
from cqparts.constraint import Mate

class Cylinder(cqparts.Part):
    diam = PositiveFloat(10, doc="cylinder's diameter")
    length = PositiveFloat(10, doc="cylinder's length")
    embed = PositiveFloat(2, doc="embedding distance")
    hole_diam = PositiveFloat(2.72, doc="pilot hole diam")

    _render = render_props(alpha=0.8)

    def make_base_cylinder(self):
        # This is used as a basis for make() and cutaway()
        return cadquery.Workplane('XY') \
            .circle(self.diam/2).extrude(self.embed + self.length)

    def make(self):
        # Use the base cylindrical shape, and cut a hole through it
        return self.make_base_cylinder() \
            .faces(">Z").hole(self.hole_diam / 2)

    @property
    def cutaway(self):
        # Use the base cylindrical shape, no alterations
        return self.make_base_cylinder()

    @property
    def mate_embedded(self):
        return Mate(self, CoordSystem((0, 0, self.embed)))


# -------------------------- Plate Part --------------------------

from math import sin, cos, radians

class Plate(cqparts.Part):
    length = PositiveFloat(20, doc="plate length")
    width = PositiveFloat(20, doc="plate width")
    thickness = PositiveFloat(10, doc="plate thickness")
    hole_diam = PositiveFloat(3, doc="hole diameter")
    connection_offset = Float(4, doc="hole's offset from plate center along x-axis")
    connection_angle = Float(15, doc="angle of mate point")

    def make(self):
        plate = cadquery.Workplane('XY') \
            .box(self.length, self.width, self.thickness)
        hole_tool = cadquery.Workplane('XY', origin=(0, 0, -self.thickness * 5)) \
            .circle(self.hole_diam / 2).extrude(self.thickness * 10)
        hole_tool = self.mate_hole.local_coords + hole_tool
        return plate.cut(hole_tool)

    @property
    def mate_hole(self):
        return Mate(self, CoordSystem(
            origin=(self.connection_offset, 0, self.thickness/2),
            xDir=(1, 0, 0),
            normal=(0, -sin(radians(self.connection_angle)), cos(radians(self.connection_angle))),
        ))

# -------------------------- Demo Assembly --------------------------

from cqparts.constraint import Fixed, Coincident

class Thing(cqparts.Assembly):

    # Components are updated to self.components first
    def make_components(self):
        return {
            'pla': Plate(),
            'cyl': Cylinder(),
        }

    # Then constraints are appended to self.constraints (second)
    def make_constraints(self):
        plate = self.components['pla']
        cylinder = self.components['cyl']
        return [
            Fixed(
                mate=plate.mate_origin,
                world_coords=CoordSystem(origin=(-1,-5,-2), xDir=(-0.5,1,0))  # a bit of random placement
            ),
            Coincident(
                mate=cylinder.mate_embedded,
                to_mate=plate.mate_hole,
            ),
        ]

    # In between updating components, and adding constraints:
    #   self.solve() is run.
    # This gives each component a valid world_coords value, so
    # we can use it in the next step...

    # Lastly, this function is run (any return is ignored)
    def make_alterations(self):
        # get Cylinder's location relative to the Plate
        coords = self.components['cyl'].world_coords - self.components['pla'].world_coords
        # apply that to the "cutout" we want to subtract from the plate
        cutout = coords + self.components['cyl'].cutaway
        self.components['pla'].local_obj = self.components['pla'].local_obj.cut(cutout)


# -------------------------- Multiple Cycles --------------------------

from cqparts.basic.primatives import Cube, Box, Sphere

class BlockStack(cqparts.Assembly):
    def make_components(self):
        print("make Box 'a'")
        yield {'a': Box(length=10, width=10, height=20)}

        print("make 2 Cubes 'b', and 'c'")
        yield {
            'b': Cube(size=8),
            'c': Cube(size=3),
        }

        print("make sphere 'd'")
        yield {'d': Sphere(radius=3)}

    def make_constraints(self):
        print("place 'a' at origin")
        a = self.components['a']
        yield [Fixed(a.mate_origin, CoordSystem((0,0,-10)))]

        print("place 'b' & 'c' relative to 'a'")
        b = self.components['b']
        c = self.components['c']
        yield [
            Fixed(b.mate_origin, a.world_coords + a.mate_pos_x.local_coords),
            Fixed(c.mate_origin, a.world_coords + a.mate_neg_y.local_coords),
        ]

        print("place sphere 'd' on cube 'b'")
        d = self.components['d']
        yield [Fixed(d.mate_origin, b.world_coords + b.mate_pos_x.local_coords)]

    def make_alterations(self):
        print("first round alteration(s)")
        yield
        print("second round alteration(s)")
        yield
        print("third round alteration(s)")
        yield


# ------------------- Export / Display -------------------
# ------- Functions
from cqparts.utils.env import get_env_name

env_name = get_env_name()

def write_file(obj, filename, world=False):
    if isinstance(obj, cqparts.Assembly):
        obj.solve()
        for (name, child) in obj.components.items():
            s = os.path.splitext(filename)
            write_file(child, "%s.%s%s" % (s[0], name, s[1]), world=True)
    else:
        print("exporting: %r" % obj)
        print("       to: %s" % filename)
        with open(filename, 'w') as fh:
            fh.write(obj.get_export_gltf(world=world))

# ------- Models
cylinder = Cylinder()
plate = Plate()
thing = Thing()
block_stack = BlockStack()

if env_name == 'cmdline':
    pass  # manually switchable for testing
    write_file(cylinder, 'cylinder.gltf')
    write_file(plate, 'plate.gltf')
    write_file(thing, 'thing.gltf')
    write_file(thing.find('pla'), 'plate-altered.gltf')
    write_file(block_stack, 'block_stack.gltf')

elif env_name == 'freecad':
    pass  # manually switchable for testing
    #display(cylinder)
    #display(plate)
    #display(thing.find('pla'))
    display(thing)
    #display(block_stack)
