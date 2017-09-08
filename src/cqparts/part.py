import cadquery
import six

from .parameter_types import t_pos_float
from .utils import indicate_last
from .errors import MakeError

class CQPartsObject(object):

    INDEX_CRITERIA = {}  # indexing criteria, used to search for parts.


class Part(CQPartsObject):

    def __init__(self, **kwargs):
        # Set part parameters
        for (k, v) in kwargs.items():
            setattr(self, k, v)

        self._object = None

    def make(self):
        """
        Create and return solid part (must be overridden in inheriting class)
        :return: cadquery.CQ (or inheriting) instance
        """
        raise NotImplementedError("make function not implemented")

    @property
    def object(self):
        # Cached
        if self._object is None:
            self._object = self.make()
            # verify
            if not isinstance(self._object, cadquery.CQ):
                raise MakeError("invalid object type returned by make(): %r" % self._object)
        return self._object

    def clear(self):
        """
        Clear internal object reference; forces object to be re-made when
        self.object is next referenced.
        """
        self._object = None

    def __copy__(self):
        return self.translate((0, 0, 0))


class Assembly(CQPartsObject):
    """
    An assembly is a group of parts, and other assemblies (called components)
    """

    def __init__(self):
        self._components = None

    def make(self):
        """
        Create and return components dict (must be overridden in inheriting class)
        :return: dict of the form: {<name>: <Part or Assembly instance>, ...}
        """
        raise NotImplementedError("make function not implemented")

    @property
    def components(self):
        if self._components is None:
            self._components = self.make()
            # verify
            if not isinstance(self._components, dict):
                raise MakeError(
                    "invalid type returned by make(): %r (must be a dict)" % self._components
                )
            else:
                for (name, component) in self._components.items():
                    if not isinstance(name, six.string_types) or not isinstance(component, (Part, Assembly)):
                        raise MakeError((
                            "invalid component returned by make(): (%r, %r) "
                            "(must be a (str, Part|Assembly))"
                        ) % (name, component))

        return self._components

    def clear(self):
        """
        Clear internal object reference; forces object to be re-made when
        self.object is next referenced.
        """
        self._components = None

    def find(self, keys, index=0):
        """
        Find a nested Assembly or Part by a '.' separated list of names.
        for example:
            >>> motor.find('bearing.outer_ring')
        would return the Part instance of the motor bearing's outer ring.
        whereas:
            >>> bearing = motor.find('bearing')
            >>> ring = bearing.find('inner_ring')  # equivalent of 'bearing.inner_ring'
        does much the same thing, bearing is an Assembly, and ring is a Part
        :param keys: str or list of key hierarchy. 'a.b' is equivalent to ['a', 'b']
        :param index: int index of keys list (used internally)
        """

        if isinstance(keys, six.string_types):
            keys = [k for k in search_str.split('.') if k]
        if index >= len(keys):
            return self

        key = keys[index]
        if key in self.components:
            component = self.components[key]
            if isinstance(component, Assembly):
                return component.find(keys, index=(index + 1))
            elif index == len(keys) - 1:
                # this is the last search key; component is a leaf, return it
                return component
            else:
                raise AssemblyFindError(
                    "could not find '%s' (invalid type at [%i]: %r)" % (
                        '.'.join(keys), index, component
                    )
                )
        else:
            raise AssemblyFindError(
                "could not find '%s', '%s' is not a component of %r" % (
                    '.'.join(keys), key, self
                )
            )

    # Component Tree
    def tree_str(self, prefix_str=''):
        """
        Return string listing recursively the assembly hierarchy
        """
        output = ''
        for (is_last, (name, component)) in indicate_last(sorted(self.components.items(), key=lambda x: x[0])):
            branch_chr = u'\u2514' if is_last else u'\u251c'
            if isinstance(component, Assembly):
                # Assembly: also list nested components
                output += prefix_str + ' ' + branch_chr + u'\u2500 ' + name + '\n'
                output += component.tree_str(
                    prefix_str=(prefix_str + (u'    ' if is_last else u' \u2502  '))
                )
            else:
                # Part (assumed): leaf node
                output += prefix_str + ' ' + branch_chr + u'\u25cb ' + name + '\n'
        return output

    def print_tree(self):
        print(repr(self))
        print(self.tree_str())


class Pulley(Part):

    # Parameter Defaults
    radius = 20.0
    width = 3.0  # contact area (not including wall thickness)
    wall_height = 1
    wall_width = 1
    hole_radius = 3.175
    key_intrusion = 0.92

    def make(self):
        # Pulley Base
        pulley_half = cadquery.Workplane("XY") \
            .circle(self.radius + self.wall_height).extrude(self.wall_width) \
            .faces(">Z").workplane() \
            .circle(self.radius).extrude(self.width / 2.0)

        # Hole
        pulley_half = pulley_half.faces(">Z").workplane() \
            .moveTo(self.hole_radius - self.key_intrusion, self.hole_radius) \
            .lineTo(0.0, self.hole_radius) \
            .threePointArc(
                (-self.hole_radius, 0.0), (0.0, -self.hole_radius)
            ) \
            .lineTo(self.hole_radius - self.key_intrusion, -self.hole_radius) \
            .close() \
            .cutThruAll()

        # Mirror half to create full pulley
        pulley = pulley_half.translate((0, 0, 0))  # copy
        pulley = pulley.union(
            pulley.translate((0, 0, 0)).mirror(
                'XY', basePointVector=(0, 0, self.wall_width + (self.width / 2.0))
            ),
        )

        return pulley


'''

print(''.join(unichr(x) for x in [0x2500, 0x2514, 0x251c, 0x2502, 0x25cb]))
─└├│○

print(u'\u2502\n\u251c\u2500\u25cb thingy\n\u251c\u2500\u2500 foo\n\u2514\u2500\u25cb bar')
│
├─○ thingy
├── foo
└─○ bar


servo
 ├─ enclosure
 │   ├○ shell
 │   ├○ end_cap
 │   └─ fasteners
 │       ├─ front_left
 │       │   ├─ bolt
 │       │   │   ├○ body
 │       │   │   └○ thread
 │       │   ├○ washer (?)
 │       │   └○ nut
 │       ├─ front_right
 │       │      ...
 │       ├─ back_left
 │       │      ...
 │       └─ back_right
 │              ...
 ├─ gearbox
 │   ├─ bearing
 │   │   ├○ outer_ring
 │   │   ├─ rolling_elements
 │   │   │   ├○ ball_1
 │   │   │   │  ...
 │   │   │   └○ ball_n
 │   │   ├○ retainer
 │   │   └○ inner_ring
 │   ├○ main_shaft
 │   ├○ middle_shaft
 │   └○ drive_shaft
 ├─ motor
 │   ├─ base_bearing ...
 │   ├─ drive_bearing ...
 │   ├─ rotor
 │   │   └○ shaft
 │   └○ stator
 └─ driver
     └○ pcb


servo = Servo(
    width=12.0,
    height=7.0,
)

display(
    servo,
    highlight=[
        servo.find('gearbox.bearing'),   # assembly (branch)
        servo.find('motor.rotor.shaft'), # part (leaf)
    ],
)
'''
