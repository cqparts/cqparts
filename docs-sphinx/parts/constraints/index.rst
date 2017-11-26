
.. _parts_constraints:

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
* one or more :class:`base.Mate` instances.
* constraint specific parameters (if any)


Types of Constraints
--------------------

Lock
^^^^

The :class:`principal.LockConstraint` explicitly sets a *component's* location
and orientation relative to its parent's origin::

    import cadquery
    from cqparts import Assembly, Part
    from cqparts.constraints import LockConstraint, Mate

    class Box(Part):
        def make():
            # a unit cube centered on 0,0,0
            return cadquery.Workplane('XY').box(1, 1, 1)

    class Thing(Assembly):
        def make():
            box1 = Box()
            box2 = Box()

            self.add_constraint(
                # box1 10mm up, no change to rotation
                LockConstraint(box1, Mate(0,0,10, (1,0,0), (0,0,1)))
            )
            self.add_constraint(
                # box2 at origin, rotate around z 45deg ccw
                LockConstraint(box2, Mate(0,0,0, (1,1,0), (0,0,1)))
            )

            return {
                'box_a': box1,
                'box_b': box2,
            }


.. warning::

    TODO: document the different types of constraints
