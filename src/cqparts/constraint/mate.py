from copy import copy
from functools import wraps

from ..utils.geometry import CoordSystem
from ..utils.misc import property_buffered


def mate(name=None):
    """
    Decorate a function as a mate

    :param name: mate name, function name used by default
    :type name: :class:`str`

    .. doctest::

        import cadquery
        import cqparts
        from cqparts.constraint.mate import mate
        from cqparts.params import *
        from cqparts.utils import CoordSystem

        class Cube(cqparts.Part):
            size = PositiveFloat(10, doc="cube's size")
            def make(self):
                return cadquery.Workplane('XY').box(*([self.size] * 3))

            @mate
            def base(self):
                return CoordSystem((0, 0, -self.size / 2))

            @mate
            def top(self, offset=0):  # mates can take parameters
                return CoordSystem((0, 0, (self.size / 2) + offset))

            @mate('side')  # mate is named 'side'
            def _mate_pos_y(self):
                return CoordSystem((0, self.size / 2, 0), xDir=(0, 1, 0))

    Each function decorated with ``@mate`` must return a
    :class:`CoordSystem <cqparts.utils.CoordSystem>` instance.

    **Calling mate from components**

    Each :class:`Component <cqparts.Component>` instance has a utility
    :meth:`mate <cqparts.Component.mate>` method to locate decorated mates
    defined for the specific component's class, and those inherited::

        >>> cube = Cube()
        >>> cube.mate('base')
        <CoordSystem: origin=(-5, 0, 0) ...>

        # Mates can use parameters
        >>> cube.mate('top', offset=0.1)
        <CoordSystem: origin=(5.1, 0, 0) ...>

        # Mates don't have to be named for their functions
        >>> cube.mate('side')
        <CoordSystem: ...>

    **Calling mate from Placed components**

    .. todo:: Mates from placed components?

    """
    func = None
    if callable(name):
        # @mate decorator was used with NO () brackets.
        func = name
        name = None

    def decorator(func):
        # Set attributes identifying this callable as a mate
        #   Why not add to a list in container class?
        #       The container class hasn't been defined yet, after all, the
        #       function being wrapped is a part of the container class.
        #       So any identification of mate classes must be done after the
        #       class is defined.
        #   See Component's metaclass for how these are used
        func._is_mate = True
        func._mate_name = name if name else func.__name__

        @wraps(func)
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            if not isinstance(ret, CoordSystem):
                raise ValueError("@mate function must return a CoordSystem, not a %r" % type(ret))
            return ret

        return inner

    return decorator(func) if func else decorator


class PlacedComponentMate(object):
    """
    A _mate_ is a coordinate system relative to a component's origin.

    ``PlacedComponentMate`` is a data class intended to pair a
    :class:`Component.Placed <cqparts.Component.Placed>` instance with a
    :class:`CoordSystem <cqparts.CoordSystem>` instance relative to the placed
    component's origin.
    """
    def __init__(self, placed_cmp, coords=None):
        """
        :param placed_cmp: placed component the mate is relative to
        :type placed_cmp: :class:`Component.Placed <cqparts.Component.Placed>`
        :param coords: coordinate system of mate relative to component's origin
        :type coords: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        """
        from ..component import Component  # avoids circular dependency

        # placed_cmp
        if isinstance(placed_cmp, Component.Placed):
            self.placed_cmp = placed_cmp
        elif placed_cmp is None:
            self.placed_cmp = None
        else:
            raise TypeError("placed_cmp must be a %r, got a %r" % (
                Component.Placed, placed_cmp,
            ))

        # coords
        if isinstance(coords, CoordSystem):
            self.coords = coords
        elif coords is None:
            self.coords = CoordSystem()
        else:
            raise TypeError("coords must be a %r, got a %r" %(
                CoordSystem, coords,
            ))

    @property_buffered
    def world_coords(self):
        """
        :return: world coordinates of mate.
        :rtype: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :raises ValueError: if ``.placed_cmp`` does not have valid world coordinates.

        If ``.placed_cmp`` is ``None``, then the ``.coords`` are returned.
        """
        if self.placed_cmp is None:
            # no placed_cmp, world == local
            return copy(self.coords)
        else:
            cmp_origin = self.placed_cmp.world_coords
            if cmp_origin is None:
                raise ValueError(
                    "mate's placed_cmp does not have world coordinates; "
                    "cannot get mate's world coordinates"
                )

            return cmp_origin + self.coords

    def __add__(self, other):
        """
        :param other: the object being added

        Behaviour based on type being added:

        :class:`Mate` + :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`:

        Return a copy of ``self`` with ``other`` added to ``.coords``

        :raises TypeError: if type of ``other`` is not supported
        """
        if isinstance(other, CoordSystem):
            return type(self)(
                placed_cmp=self.placed_cmp,
                coords=self.coords + other,
            )

        else:
            raise TypeError("addition of %r + %r is not supported" % (
                type(self), type(other)
            ))

    def __repr__(self):
        return "<{cls_name}:\n  placed_cmp={placed_cmp}\n  coords={coords}\n>".format(
            cls_name=type(self).__name__,
            placed_cmp=self.placed_cmp,
            coords=self.coords,
        )
