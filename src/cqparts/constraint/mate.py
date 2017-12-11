from copy import copy

from ..utils.geometry import CoordSystem
from ..utils.misc import property_buffered

class Mate(object):
    """
    A mate is a coordinate system relative to a component's origin.
    """
    def __init__(self, component, local_coords=None):
        """
        :param component: component the mate is relative to
        :type component: :class:`Component <cqparts.part.Component>`
        :param local_coords: coordinate system of mate relative to component's origin
        :type local_coords: :class:`CoordSystem`

        If ``component`` is explicitly set to None, the mate's
        :meth:`world_coords` == ``local_coords``.

        If ``local_coords`` is not set, the component's origin is used (ie:
        coords at ``0,0,0``, with no rotation)

        """
        from cqparts.part import Component  # avoids circular dependency

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
        :rtype: :class:`CoordSystem`
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
