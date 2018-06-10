from copy import copy
from functools import wraps

from ..utils.geometry import CoordSystem
from ..utils.misc import property_buffered


def mate(*args, **kwargs):
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
            def top(self):
                return CoordSystem((0, 0, self.size / 2))

    Each function decorated with ``@mate`` must return a
    :class:`CoordSystem <cqparts.utils.CoordSystem>` instance.
    This will be wrapped by a :class:`Mate` instance::

        >>> cube = Cube()
        >>> cube.mate('top')
        <Mate: ...>

    """
    naked = (  # was @mate decorator used with NO () brackets?
        len(args) == 1 and  # only 1 listed argument
        not kwargs and  # no keyword arguments
        callable(args[0])  # given argument is callable
    )

    # set parameters (or defaults)
    name = None
    if not naked:
        name = kwargs.get('name', name)

    def decorator(func):
        # Set attributes identifying this callable as a mate
        #   Why not add to a list in container class?
        #       The container class hasn't been defined yet, after all, the
        #       function being wrapped is a part of the container class.
        #       So any identification of mate classes must be done after the
        #       class is defined.
        func._is_mate = True
        func._mate_name = name if name else func.__name__

        @wraps(func)
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            if not isinstance(ret, Mate):
                raise ValueError("@mate function must return a Mate, not a %r" % type(ret))
            return ret

        return inner

    return decorator(args[0]) if naked else decorator


class Mate(object):
    """
    A mate is a coordinate system relative to a component's origin.
    """
    def __init__(self, component, local_coords=None):
        """
        :param component: component the mate is relative to
        :type component: :class:`Component <cqparts.Component>`
        :param local_coords: coordinate system of mate relative to component's origin
        :type local_coords: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`

        If ``component`` is explicitly set to None, the mate's
        :meth:`world_coords` == ``local_coords``.

        If ``local_coords`` is not set, the component's origin is used (ie:
        coords at ``0,0,0``, with no rotation)

        """
        from ..component import Component  # avoids circular dependency

        # component
        if isinstance(component, Component):
            self.component = component
        elif component is None:
            self.component = None
        else:
            raise TypeError("component must be a %r, got a %r" % (Component, component))

        # local_coords
        if isinstance(local_coords, CoordSystem):
            self.local_coords = local_coords
        elif local_coords is None:
            self.local_coords = CoordSystem()
        else:
            raise TypeError("local_coords must be a %r, got a %r" %(CoordSystem, local_coords))

    @property_buffered
    def world_coords(self):
        """
        :return: world coordinates of mate.
        :rtype: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :raises ValueError: if ``.component`` does not have valid world coordinates.

        If ``.component`` is ``None``, then the ``.local_coords`` are returned.
        """
        if self.component is None:
            # no component, world == local
            return copy(self.local_coords)
        else:
            cmp_origin = self.component.world_coords
            if cmp_origin is None:
                raise ValueError(
                    "mate's component does not have world coordinates; "
                    "cannot get mate's world coordinates"
                )

            return cmp_origin + self.local_coords

    def __add__(self, other):
        """
        :param other: the object being added

        Behaviour based on type being added:

        :class:`Mate` + :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`:

        Return a copy of ``self`` with ``other`` added to ``.local_coords``

        :raises TypeError: if type of ``other`` is not supported
        """
        if isinstance(other, CoordSystem):
            return type(self)(
                component=self.component,
                local_coords=self.local_coords + other,
            )

        else:
            raise TypeError("addition of %r + %r is not supported" % (
                type(self), type(other)
            ))

    def __repr__(self):
        return "<{cls_name}:\n  component={component}\n  local_coords={local_coords}\n>".format(
            cls_name=type(self).__name__,
            component=self.component,
            local_coords=self.local_coords,
        )
