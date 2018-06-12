import six
from copy import copy

from .params import ParametricObject
from .constraint.mate import mate, PlacedComponentMate
from .utils import CoordSystem


class ComponentMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # Mate Map:
        #   find @mate decorated methods, map them to _mate_map attribute
        # inherit
        _mate_map = {}
        for base in reversed(bases):
            _mate_map.update(copy(getattr(base, '_mate_map', {})))
        # local
        _mate_map.update({
            value._mate_name: key
            for (key, value) in attrs.items()
            if getattr(value, '_is_mate', False)
        })
        attrs['_mate_map'] = _mate_map

        return super(ComponentMetaclass, cls).__new__(cls, name, bases, attrs)


@six.add_metaclass(ComponentMetaclass)
class Component(ParametricObject):
    """
    .. note::

        Both the :class:`Part` and :class:`Assembly` classes inherit
        from ``Component``.

        Wherever the term "*component*" is used, it is in reference to an
        instance of either :class:`Part` **or** :class:`Assembly`.
    """

    def build(self, recursive=True):
        """
        :raises NotImplementedError: must be overridden by inheriting classes to function
        """
        raise NotImplementedError("build not implemented for %r" % type(self))

    @mate('origin')
    def _mate_origin(self):
        return CoordSystem()

    def mate(self, name, *args, **kwargs):
        """
        Gets the :class:`CoordSystem` return of a
        :meth:`@mate <cqparts.constraint.mate.mate>` decorated function.

        Read the :meth:`@mate <cqparts.constraint.mate.mate>` decorator's
        documentation for examples.
        """
        func_name = self._mate_map[name]
        return getattr(self, func_name)(*args, **kwargs)

    def mate_names(self):
        return self._mate_map.keys()

    # ----- Export / Import
    def exporter(self, exporter_name=None):
        """
        Get an exporter instance to write the component's content to file.

        :param exporter_name: registered name of exporter to use, see
                              :meth:`register_exporter() <cqparts.codec.register_exporter>`
                              for more information.
        :type exporter_name: :class:`str`

        For example, to get a
        :class:`ThreejsJSONExporter <cqparts.codec.ThreejsJSONExporter>`
        instance to import a ``json`` file:

        .. doctest::

            >>> from cqparts_misc.basic.primatives import Box
            >>> box = Box()
            >>> json_exporter = box.exporter('json')

            >>> # then each exporter will behave differently
            >>> json_exporter('out.json')  # doctest: +SKIP

        To learn more: :ref:`parts_import-export`
        """
        from .codec import get_exporter
        return get_exporter(self, exporter_name)

    @classmethod
    def importer(cls, importer_name=None):
        """
        Get an importer instance to instantiate a component from file.

        :param importer_name: registered name of importer to use, see
                              :meth:`register_importer() <cqparts.codec.register_importer>`
                              for more information.
        :type importer_name: :class:`str`

        For example, to get an importer to instantiate a :class:`Part` from a
        ``STEP`` file:

        .. doctest::

            >>> from cqparts import Part
            >>> step_importer = Part.importer('step')

            >>> # then each importer will behave differently
            >>> my_part = step_importer('my_file.step')  # doctest: +SKIP

        To learn more: :ref:`parts_import-export`
        """
        from .codec import get_importer
        return get_importer(cls, importer_name)

    class Placed(object):
        """
        A wrapper to a :class:`Component` to apply translation & rotation.
        """

        def __init__(self, wrapped, coords=None, parent=None):
            """
            :param wrapped: wrapped component
            :type wrapped: :class:`Component`
            :param coords: component placement (translation & rotation from origin)
            :type coords: :class:`CoordSystem <cqparts.utils.CoordSystem>`
            :param parent: parent :class:`Component.Placed` or ``None``
            :type parent: :class:`Component.Placed`
            """
            if not isinstance(component, Component):
                raise ValueError("componnet must be a Component class, not a %r" % type(component))

            self.wrapped = component
            self.parent = parent
            self._coords = coords

        # --- Coordinate Systems
        # Placement coords
        @property
        def coords(self):
            """
            Component's placement in word coordinates
            (:class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`)

            :return: coordinate system in the world, ``None`` if not set.
            :rtype: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
            """
            return self._coords

        @coords.setter
        def coords(self, value):
            if not isinstance(value, CoordSystem):
                raise ValueError("set value must be a %r, not a %r" % (CoordSystem, type(value)))
            if self._coords != value:
                self._coords = value
                self._placement_changed()
            # else: if coordinates are not being changed, don't do anything

        # World coordinates
        @property
        def world_coords(self):
            """
            This placed component's coordinate system in the world.
            A coordinate system accumulated from all ancestors, starting with
            this instances ``parent``.
            """
            if self.parent is None:
                # no parent; this component is the trunk
                return self.coords
            return self.parent.coords + self.coords

        # --- Mate
        def mate(self, name, *args, **kwargs):
            mate_coords = self.wrapped.mate(name, *args, **kwargs)
            return PlacedComponentMate(self, mate_coords)

        # --- Callbacks
        def _placement_changed(self):
            # called when self.coords is set
            # (intended to be overridden by inheriting classes)
            pass
