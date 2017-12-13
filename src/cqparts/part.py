import cadquery
import six
from copy import copy
from io import BytesIO
import json
from types import GeneratorType

from .params import ParametricObject, Boolean
from .utils.misc import indicate_last, property_buffered
from .display import (
    RenderParam,
    TEMPLATE as RENDER_TEMPLATE,
)
from .errors import MakeError, ParameterError, AssemblyFindError
from .constraint import Constraint, Mate
from .constraint.solver import solver

from .utils.geometry import copy as copy_wp
from .utils.geometry import CoordSystem

import logging
log = logging.getLogger(__name__)


class Component(ParametricObject):
    """
    .. note::

        Both the :class:`Part` and :class:`Assembly` classes inherit
        from ``Component``.

        Wherever the term "*component*" is used, it is in reference to an
        instance of either :class:`Part` **or** :class:`Assembly`.
    """

    def __init__(self, *largs, **kwargs):
        super(Component, self).__init__(*largs, **kwargs)

        # Initializing Instance State
        self._world_coords = None

    def build(self, recursive=True):
        """
        :raises NotImplementedError: must be overridden by inheriting classes to function
        """
        raise NotImplementedError("build not implemented for %r" % type(self))

    def _placement_changed(self):
        # called when:
        #   - world_coords is set
        # (intended to be overridden by inheriting classes)
        pass

    @property
    def world_coords(self):
        """
        Component's placement in word coordinates
        (:class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`)

        :return: coordinate system in the world, ``None`` if not set.
        :rtype: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        """
        return self._world_coords

    @world_coords.setter
    def world_coords(self, value):
        self._world_coords = value
        self._placement_changed()

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

            >>> from cqparts.basic.primatives import Box
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
            >>> my_part = step_importer('my_file.step')

        To learn more: :ref:`parts_import-export`
        """
        from .codec import get_importer
        return get_importer(cls, importer_name)


class Part(Component):

    # Parameters common to every Part
    _simple = Boolean(False, doc="if set, simplified geometry is built")
    _render = RenderParam(RENDER_TEMPLATE['default'], doc="render properties")

    def __init__(self, *largs, **kwargs):
        super(Part, self).__init__(*largs, **kwargs)

        # Initializing Instance State
        self._local_obj = None
        self._world_obj = None

    def make(self):
        """
        Create and return solid part

        :return: cadquery.Workplane of the part in question
        :rtype: subclass of :class:`cadquery.CQ`, usually a :class:`cadquery.Workplane`

        .. important::
            This must be overridden in your ``Part``

        The outcome of this function should be accessed via cqparts.Part.object
        """
        raise NotImplementedError("make function not implemented")

    def make_simple(self):
        """
        Create and return *simplified* solid part.

        The simplified representation of a ``Part`` is to lower the export
        quality of an ``Assembly`` or ``Part`` for rendering.

        Overriding this is optional, but highly recommended.

        The default behaviour returns the full complexity object's bounding box.
        But to do this, theh full complexity object must be generated first.

        There are 2 main problems with this:

        #. building the full complexity part is not efficient.
        #. a bounding box may not be a good representation of the part.

        **Bolts**

        A good example of this is a bolt.

        * building a bolt's thread is not a trivial task;
          it can take some time to generate.
        * a box is not a good visual representation of a bolt

        So for the ``Fastener`` parts, all ``make_simple`` methods are overridden
        to provide 2 cylinders, one for the bolt's head, and another for the thread.
        """
        complex_obj = self.make()
        bb = complex_obj.findSolid().BoundingBox()
        simple_obj = cadquery.Workplane('XY', origin=(bb.xmin, bb.ymin, bb.zmin)) \
            .box(bb.xlen, bb.ylen, bb.zlen, centered=(False, False, False))
        return simple_obj

    def build(self, recursive=False):
        """
        Building a part buffers the ``local_obj`` attribute.

        Running ``.build()`` is optional, it's mostly used to test that
        there aren't any critical runtime issues with it's construction.

        :param recursive: (:class:`Part` has no children, parameter ignored)
        """
        self.local_obj  # force object's construction, but don't do anything with it

    # ----- Local Object
    @property
    def local_obj(self):
        """
        Buffered result of :meth:`cqparts.Part.make` which is (probably) a
        :class:`cadquery.Workplane` instance.

        .. note::
            This is usually the correct way to get your part's object
            for rendering, exporting, or measuring.

            Only call :meth:`cqparts.Part.make` directly if you explicitly intend
            to re-generate the model from scratch, then dispose of it.
        """
        if self._local_obj is None:
            # Simplified or Complex
            if self._simple:
                value = self.make_simple()
            else:
                value = self.make()
            # Verify type
            if not isinstance(value, cadquery.CQ):
                raise MakeError("invalid object type returned by make(): %r" % value)
            # Buffer object
            self._local_obj = value
        return self._local_obj

    @local_obj.setter
    def local_obj(self, value):
        self._local_obj = value
        self._world_obj = None

    # ----- World Object
    @property
    def world_obj(self):
        """
        The :meth:`local_obj <local_obj>` object in the
        :meth:`world_coords <Component.world_coords>` coordinate system.

        .. note::

            This is automatically generated when called, and
            :meth:`world_coords <Component.world_coords>` is not ``Null``.
        """
        if self._world_obj is None:
            local_obj = self.local_obj
            world_coords = self.world_coords
            if (local_obj is not None) and (world_coords is not None):
                # Copy local object, apply transform to move to its new home.
                self._world_obj = world_coords + local_obj
        return self._world_obj

    @world_obj.setter
    def world_obj(self, value):
        # implemented just for this helpful message
        raise ValueError("can't set world_obj directly, set local_obj instead")

    @property
    def bounding_box(self):
        """
        Generate a bounding box based on the full complexity part.

        :return: bounding box of part
        :rtype: cadquery.BoundBox
        """
        return self.local_obj.findSolid().BoundingBox()

    def _placement_changed(self):
        self._world_obj = None

    def __copy__(self):
        new_obj = super(Part, self).__copy__()
        # copy private content
        new_obj._local_obj = copy_wp(self._local_obj)
        new_obj._world_coords = copy(self._world_coords)
        new_obj._world_obj =  copy_wp(self._world_obj)

        return new_obj


class Assembly(Component):
    """
    An assembly is a group of parts, and other assemblies (called components)
    """

    def __init__(self, *largs, **kwargs):
        super(Assembly, self).__init__(*largs, **kwargs)
        self._components = None
        self._constraints = None

    def make_components(self):
        """
        Create and return :class:`dict` of :class:`Component` instances.

        .. tip::

            This **must** be overridden in inheriting class, read:

            * :ref:`parts_assembly-build-cycle` for details.
            * :ref:`tutorial_assembly` for an example.

        :return: {<name>: <Component>, ...}
        :rtype: :class:`dict` of :class:`Component` instances
        """
        raise NotImplementedError("make_components function not implemented")

    def make_constraints(self):
        """
        Create and return :class:`list` of
        :class:`Constraint <cqparts.constraint.base.Constraint>` instances

        .. tip::

            This **must** be overridden in inheriting class, read:

            * :ref:`parts_assembly-build-cycle` for details.
            * :ref:`tutorial_assembly` for an example.

        :return: constraints for assembly children's placement
        :rtype: :class:`list` of :class:`Constraint <cqparts.constraint.base.Constraint>` instances

        Default behaviour returns an empty list; assumes assembly is
        entirely unconstrained.
        """
        raise NotImplementedError("make_constraints function not implemented")

    def make_alterations(self):
        """
        Make necessary changes to components after the constraints solver has
        completed.

        .. tip::

            This *can* be overridden in inheriting class, read:

            * :ref:`parts_assembly-build-cycle` for details.
            * :ref:`tutorial_assembly` for an example.

        """
        pass

    @property
    def components(self):
        """
        Returns full :class:`dict` of :class:`Component` instances, after
        a successful :meth:`build`

        :return: dict of named :class:`Component` instances
        :rtype: :class:`dict`

        For more information read about the :ref:`parts_assembly-build-cycle` .
        """
        if self._components is None:
            self.build(recursive=False)
        return self._components

    @property
    def constraints(self):
        """
        Returns full :class:`list` of :class:`Constraint <cqparts.constraint.Constraint>` instances, after
        a successful :meth:`build`

        :return: list of named :class:`Constraint <cqparts.constraint.Constraint>` instances
        :rtype: :class:`list`

        For more information read about the :ref:`parts_assembly-build-cycle` .
        """
        if self._constraints is None:
            self.build(recursive=False)
        return self._constraints

    def _placement_changed(self):
        """
        Called when ``world_coords`` is changed.

        All components' ``world_coords`` must be updated based on the change;
        calls :meth:`solve`.
        """
        self.solve()

    def solve(self):
        """
        Run the solver and assign the solution's :class:`CoordSystem` instances
        as the corresponding part's world coordinates.
        """
        if self.world_coords is None:
            log.warning("solving for Assembly without word coordinates set: %r", self)

        for (component, world_coords) in solver(self.constraints, self.world_coords):
            component.world_coords = world_coords

    @staticmethod
    def verify_components(components):
        """
        Verify values returned from :meth:`make_components`.

        Used internally during the :meth:`build` process.

        :param components: value returned from :meth:`make_components`
        :type components: :class:`dict`
        :raises ValueError: if verification fails
        """
        # verify returned type from user-defined function
        if not isinstance(components, dict):
            raise ValueError(
                "invalid type returned by make_components(): %r (must be a dict)" % components
            )

        # check types for (name, component) pairs in dict
        for (name, component) in components.items():
            # name is a string
            if not isinstance(name, six.string_types):
                raise ValueError((
                    "invalid name from make_components(): (%r, %r) "
                    "(must be a (str, Component))"
                ) % (name, component))

            # component is a Component instance
            if not isinstance(component, Component):
                raise ValueError((
                    "invalid component type from make_components(): (%r, %r) "
                    "(must be a (str, Component))"
                ) % (name, component))

            # name cannot contain a '.'
            if '.' in name:
                raise ValueError("component names cannot contain a '.' (%s, %r)" % (name, component))

    @staticmethod
    def verify_constraints(constraints):
        """
        Verify values returned from :meth:`make_constraints`.

        Used internally during the :meth:`build` process.

        :param constraints: value returned from :meth:`make_constraints`
        :type constraints: :class:`list`
        :raises ValueError: if verification fails
        """
        # verify return is a list
        if not isinstance(constraints, list):
            raise ValueError(
                "invalid type returned by make_constraints: %r (must be a list)" % constraints
            )

        # verify each list element is a Constraint instance
        for constraint in constraints:
            if not isinstance(constraint, Constraint):
                raise ValueError(
                    "invalid constraint type: %r (must be a Constriant)" % constraint
                )

    def build(self, recursive=True):
        """
        Building an assembly buffers the :meth:`components` and :meth:`constraints`.


        Running ``build()`` is optional, it's automatically run when requesting
        :meth:`components` or :meth:`constraints`.

        Mostly it's used to test that there aren't any critical runtime
        issues with it's construction, but doing anything like *displaying* or
        *exporting* will ultimately run a build anyway.

        :param recursive: if set, iterates through child components and builds
                          those as well.
        :type recursive: :class:`bool`
        """

        # initialize values
        self._components = {}
        self._constraints = []

        def genwrap(obj, name, iter_type=None):
            # Force obj to act like a generator.
            # this wrapper will always yield at least once.
            if isinstance(obj, GeneratorType):
                for i in obj:
                    if (iter_type is not None) and (not isinstance(i, iter_type)):
                        raise TypeError("%s must yield a %r" % (name, iter_type))
                    yield i
            else:
                if (iter_type is not None) and (not isinstance(obj, iter_type)):
                    raise TypeError("%s must return a %r" % (name, iter_type))
                yield obj

        # Make Components
        components_iter = genwrap(self.make_components(), "make_components", dict)
        new_components = components_iter.next()
        self.verify_components(new_components)
        self._components.update(new_components)

        # Make Constraints
        constraints_iter = genwrap(self.make_constraints(), "make_components", list)
        new_constraints = constraints_iter.next()
        self.verify_constraints(new_constraints)
        self._constraints += new_constraints

        # Run solver : sets components' world coordinates
        self.solve()

        # Make Alterations
        alterations_iter = genwrap(self.make_alterations(), "make_alterations")
        alterations_iter.next()  # return value is ignored

        while True:
            (s1, s2, s3) = (True, True, True)  # stages
            # Make Components
            try:
                new_components = components_iter.next()
                self.verify_components(new_components)
                self._components.update(new_components)
            except StopIteration:
                s1 = False

            # Make Constraints
            try:
                new_constraints = constraints_iter.next()
                self.verify_constraints(new_constraints)
                self._constraints += new_constraints
            except StopIteration:
                s2 = False

            # Run solver : sets components' world coordinates
            self.solve()

            # Make Alterations
            try:
                alterations_iter.next()  # return value is ignored
            except StopIteration:
                s3 = False

            # end loop when all iters are finished
            if not any((s1, s2, s3)):
                break

        if recursive:
            for (name, component) in self._components.items():
                component.build(recursive=recursive)

    def find(self, keys, _index=0):
        """
        :param keys: key path. ``'a.b'`` is equivalent to ``['a', 'b']``
        :type keys: :class:`str` or :class:`list`

        Find a nested :class:`Component` by a "`.`" separated list of names.
        for example::

            >>> motor.find('bearing.outer_ring')

        would return the Part instance of the motor bearing's outer ring.

        ::

            >>> bearing = motor.find('bearing')
            >>> ring = bearing.find('inner_ring')  # equivalent of 'bearing.inner_ring'

        the above code does much the same thing, ``bearing`` is an :class:`Assembly`,
        and ``ring`` is a :class:`Part`.

        .. note::

            For a key path of ``a.b.c`` the ``c`` key can referernce any
            :class:`Component` type.

            Everything prior (in this case ``a`` and ``b``) must reference an
            :class:`Assembly`.
        """

        if isinstance(keys, six.string_types):
            keys = [k for k in keys.split('.') if k]
        if _index >= len(keys):
            return self

        key = keys[_index]
        if key in self.components:
            component = self.components[key]
            if isinstance(component, Assembly):
                return component.find(keys, _index=(_index + 1))
            elif _index == len(keys) - 1:
                # this is the last search key; component is a leaf, return it
                return component
            else:
                raise AssemblyFindError(
                    "could not find '%s' (invalid type at [%i]: %r)" % (
                        '.'.join(keys), _index, component
                    )
                )
        else:
            raise AssemblyFindError(
                "could not find '%s', '%s' is not a component of %r" % (
                    '.'.join(keys), key, self
                )
            )

    # Component Tree
    def tree_str(self, name=None, prefix_str='', add_repr=False, _depth=0):
        u"""
        Return string listing recursively the assembly hierarchy

        :param name: if set, names the tree's trunk, otherwise the object's :meth:`repr` names the tree
        :type name: :class:`str`
        :param prefix_str: string prefixed to each line, can be used to indent
        :type prefix_str: :class:`str`
        :param add_repr: if set, *component* :meth:`repr` is put after their names
        :type add_repr: :class:`bool`
        :return: Printable string of an assembly's component hierarchy.
        :rtype: :class:`str`

        Example output from `block_tree.py <https://github.com/fragmuffin/cqparts/blob/master/tests/manual/block_tree.py>`_

        ::

            >>> log = logging.getLogger(__name__)
            >>> isinstance(block_tree, Assembly)
            True
            >>> log.info(block_tree.tree_str(name="block_tree"))
            block_tree
             \u251c\u25cb branch_lb
             \u251c\u25cb branch_ls
             \u251c\u2500 branch_r
             \u2502   \u251c\u25cb L
             \u2502   \u251c\u25cb R
             \u2502   \u251c\u25cb branch
             \u2502   \u251c\u2500 house
             \u2502   \u2502   \u251c\u25cb bar
             \u2502   \u2502   \u2514\u25cb foo
             \u2502   \u2514\u25cb split
             \u251c\u25cb trunk
             \u2514\u25cb trunk_split

        Where:

        * ``\u2500`` denotes an :class:`Assembly`, and
        * ``\u25cb`` denotes a :class:`Part`
        """

        # unicode characters
        c_t = u'\u251c'
        c_l = u'\u2514'
        c_dash = u'\u2500'
        c_o = u'\u25cb'
        c_span = u'\u2502'

        output = u''
        if not _depth:  # first line
            output = unicode(prefix_str)
            if name:
                output += (name + u': ') if add_repr else name
            if add_repr or not name:
                output += repr(self)
            output += '\n'

        # build tree
        for (is_last, (name, component)) in indicate_last(sorted(self.components.items(), key=lambda x: x[0])):
            branch_chr = c_l if is_last else c_t
            if isinstance(component, Assembly):
                # Assembly: also list nested components
                output += prefix_str + ' ' + branch_chr + c_dash + u' ' + name
                if add_repr:
                    output += ': ' + repr(component)
                output += '\n'
                output += component.tree_str(
                    prefix_str=(prefix_str + (u'    ' if is_last else (u' ' + c_span + '  '))),
                    add_repr=add_repr,
                    _depth=_depth + 1,
                )
            else:
                # Part (assumed): leaf node
                output += prefix_str + ' ' + branch_chr + c_o + u' ' + name
                if add_repr:
                    output += ': ' + repr(component)
                output += '\n'
        return output
