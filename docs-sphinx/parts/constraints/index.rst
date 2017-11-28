
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

    import cadquery
    from cqparts import Assembly, Part
    from cqparts.constraints import LockConstraint, Mate

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
                # box1 10mm up, no change to rotation
                LockConstraint(self.components['box_a'], Mate(0,0,10, (1,0,0), (0,0,1))),
                # box2 at origin, rotate around z 45deg ccw
                LockConstraint(self.components['box_b'], Mate(0,0,0, (1,1,0), (0,0,1))),
            ]

    thing = Thing()
    thing.build()  # creates and places all components recursively

.. warning::

    TODO: document the different types of constraints
