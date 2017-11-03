import cadquery
import six

from .params import ParametricObject
from .utils import indicate_last
from .errors import MakeError, ParameterError


class Part(ParametricObject):

    def __init__(self, *largs, **kwargs):
        super(Part, self).__init__(*largs, **kwargs)
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
        calling clear() is unnecessary if the object is acquired with make().
        """
        self._object = None

    def __copy__(self):
        new_obj = super(Part, self).__copy__()
        if new_obj._object is not None:
            new_obj._object = self._object.translate((0, 0, 0))
        return new_obj


class Assembly(ParametricObject):
    """
    An assembly is a group of parts, and other assemblies (called components)
    """

    def __init__(self, *largs, **kwargs):
        super(Assembly, self).__init__(*largs, **kwargs)
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
