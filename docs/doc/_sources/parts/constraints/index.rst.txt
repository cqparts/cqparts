
.. _parts.constraints:

.. currentmodule:: cqparts.constraints

Constraints
===========

Constraints limit the location & orientation of a :class:`Component <cqparts.part.Component>`
relative to its parent :class:`Assembly <cqparts.part.Assembly>`.

A completely unconstrained *component* could be anywhere, and with any rotation.
Conversely, a fully constrained *component* can only be at one specific location
& orientation.

Constraints consist of, at a minimum:

* the :class:`Component <cqparts.part.Component>` being constrained.
* one or more :class:`Mate <mate.Mate>` instances.
* constraint specific parameters (if any)


Types of Constraints
--------------------

Lock
^^^^

The :class:`LockConstraint <lock.LockConstraint>` explicitly sets a *component's* location
and orientation relative to its parent's origin:

.. doctest::

    >>> import cadquery
    >>> from cqparts import Assembly, Part
    >>> from cqparts.constraints.lock import LockConstraint, Mate

    >>> class Box(Part):
    ...     def make(self):
    ...         # a unit cube centered on 0,0,0
    ...         return cadquery.Workplane('XY').box(1, 1, 1)

    >>> class Thing(Assembly):
    ...     def make_components(self):
    ...         return {
    ...             'box_a': Box(),
    ...             'box_b': Box(),
    ...         }
    ...
    ...     def make_constraints(self):
    ...         return [
    ...             # boxA 10mm up, no change to rotation
    ...             LockConstraint(self.components['box_a'], Mate((0,0,10), (1,0,0), (0,0,1))),
    ...             # boxA at origin, rotate around z 45deg ccw
    ...             LockConstraint(self.components['box_b'], Mate((0,0,0), (1,1,0), (0,0,1))),
    ...         ]

    >>> thing = Thing()
    >>> thing.build()  # creates and places all components recursively


RelativeLock
^^^^^^^^^^^^

The :class:`RelativeLockConstraint <lock.RelativeLockConstraint>` sets a
*component's* coordinate system relative to another part's world coordinate
system.

In order to solve a relative offset, the relative coordinates need to be
solved first. So for the coordinates ``A + B = C``, where:

* ``A`` is the ``relative_to`` object's coordinate system.
* ``B`` is the offset (explicitly set; always known)
* ``C`` is the coordinate system being solved.

We can only know what ``C`` is if we know the values of both ``A`` and ``B``.

.. doctest::

    >>> import cadquery
    >>> from cqparts import Assembly, Part
    >>> from cqparts.constraints.lock import (
    ...     LockConstraint, RelativeLockConstraint, Mate
    ... )

    >>> class Box(Part):
    ...     def make(self):
    ...         # a unit cube placed on top of XY plane
    ...         return cadquery.Workplane('XY') \
    ...             .box(10, 10, 10, centered=(True, True, False))
    ...
    ...     @property
    ...     def mate_top(self):
    ...         return Mate.from_plane(self.local_obj.faces(">Z").workplane().plane)

    >>> class Thing(Assembly):
    ...     def make_components(self):
    ...         return {
    ...             'box_a': Box(),
    ...             'box_b': Box(),
    ...         }
    ...
    ...     def make_constraints(self):
    ...         return [
    ...             # boxA at zero, no rotation
    ...             LockConstraint(
    ...                 self.components['box_a'], Mate((0,0,0), (1,0,0), (0,0,1))
    ...             ),
    ...             # boxB at on top of boxA, using boxA's
    ...             RelativeLockConstraint(
    ...                 component=self.components['box_b'],
    ...                 mate=self.components['box_a'].mate_top,
    ...                 relative_to=self.components['box_a'],
    ...             ),
    ...         ]

    >>> thing = Thing()
    >>> thing.build()  # creates and places all components recursively


.. warning::

    TODO: document the different types of constraints
