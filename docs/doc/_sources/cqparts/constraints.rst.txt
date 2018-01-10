
.. _parts.constraints:

.. currentmodule:: cqparts.constraint

Constraints
===========

Constraints limit the location & orientation of a :class:`Component <cqparts.Component>`
relative to its parent :class:`Assembly <cqparts.Assembly>`.

A completely unconstrained *component* could be anywhere, and with any rotation.
Conversely, a fully constrained *component* can only be at one specific location
& orientation.

Constraints consist of, at a minimum:

* the :class:`Component <cqparts.Component>` being constrained.
* one or more :class:`Mate` instances.
* constraint specific parameters (if any)


Types of Constraints
-----------------------

Fixed
^^^^^^^^

The :class:`Fixed` explicitly sets a *component's* location
and orientation relative to its parent's origin:

.. testcode::

    import cadquery
    from cqparts import Assembly, Part
    from cqparts.constraint import Fixed
    from cqparts.utils.geometry import CoordSystem

    class Box(Part):
        def make(self):
            # a unit cube centered on 0,0,0
            return cadquery.Workplane('XY').box(1, 1, 1)

    class Thing(Assembly):
        def make_components(self):
            return {
                'box_a': Box(),
                'box_b': Box(),
            }

        def make_constraints(self):
            return [
                Fixed(  # boxA 10mm up, no change to rotation
                    self.components['box_a'].mate_origin,
                    CoordSystem((0,0,10), (1,0,0), (0,0,1))
                ),

                Fixed(  # boxB at origin, rotate around z 45deg ccw
                    self.components['box_b'].mate_origin,
                    CoordSystem((0,0,0), (1,1,0), (0,0,1))
                ),
            ]

    thing = Thing()
    thing.build()  # creates and places all components recursively


Coincident
^^^^^^^^^^^^^^^

The :class:`Coincident` sets a
*component's* coordinate system relative to another part's world coordinate
system.

In order to solve a relative offset, the relative coordinates need to be
solved first. So for the coordinates ``A + B = C``, where:

* ``A`` is the ``relative_to`` object's coordinate system.
* ``B`` is the offset (explicitly set; always known)
* ``C`` is the coordinate system being solved.

We can only know what ``C`` is if we know the values of both ``A`` and ``B``.

.. testcode::

    import cadquery
    from cqparts import Assembly, Part
    from cqparts.constraint import (
        Fixed, Coincident, Mate
    )
    from cqparts.utils.geometry import CoordSystem

    class Box(Part):
        def make(self):
            # a unit cube placed on top of XY plane
            return cadquery.Workplane('XY') \
                .box(10, 10, 10, centered=(True, True, False))

        @property
        def mate_top(self):
            return Mate(self, CoordSystem.from_plane(
                self.local_obj.faces(">Z").workplane().plane
            ))

    class Thing(Assembly):
        def make_components(self):
            return {
                'box_a': Box(),
                'box_b': Box(),
            }

        def make_constraints(self):
            return [
                # boxA at zero, no rotation
                Fixed(self.components['box_a'].mate_origin),
                # boxB at on top of boxA, using boxA's mate_top attribute
                Coincident(
                    self.components['box_b'].mate_origin,
                    self.components['box_a'].mate_top,
                ),
            ]

    thing = Thing()
    thing.build()  # creates and places all components recursively


More...
^^^^^^^^^^^^^^^

.. warning::

    At this time only 6dof locking constraints are available.

    More are planned to be introduced in
    `issue #30 <https://github.com/fragmuffin/cqparts/issues/30>`_.

    Please feel free to post your interest there to help us gauge how high the
    priority should be on this improvement.

    Examples are most welcome.
