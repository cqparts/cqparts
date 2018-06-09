from .params import ParametricObject
from .constraint import Mate
from .utils import CoordSystem


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

    @property
    def mate_origin(self):
        """
        :return: mate at object's origin
        :rtype: :class:`Mate`
        """
        return Mate(self, CoordSystem())

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

        def __init__(self, wrapped, *args, **kwargs):
            """
            :param wrapped: wrapped component
            :type wrapped: :class:`Component`
            :param parent: parent :class:`Component.Placed`
            :type parent: :class:`Component.Placed`
            """
            if not isinstance(component, Component):
                raise ValueError("componnet must be a Component class, not a %r" % type(component))
            self.wrapped = component

            self.parent = kwargs.pop('parent', None)

            # location, defaults to a coordinate system at the origin
            self._coords = CoordSystem(*args, **kwargs)

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

        # --- Callbacks
        def _placement_changed(self):
            # called when self.coords is set
            # (intended to be overridden by inheriting classes)
            pass
