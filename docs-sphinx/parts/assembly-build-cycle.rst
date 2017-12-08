
.. currentmodule:: cqparts.part

.. _parts_assembly-build-cycle:

``Assembly`` Build Cycle
==========================

If a :class:`Part` is a blueprint for an *atomic* component, then an
:class:`Assembly` is a blueprint for, not just where those components fit together,
but also the routine to determining *how* they fit together, and how
they may be *altered* to be assembled.

An :class:`Assembly` is built in the following order:

#. add components (with :meth:`make_components() <Assembly.make_components>`)
#. add constraints (with :meth:`make_constraints() <Assembly.make_constraints>`)
#. solve constraints (places components)
#. alter parts (with :meth:`make_alterations() <Assembly.make_alterations>`)
#. go back to step 1 (more on this in :ref:`parts_assembly-build-cycle_multiple`)


Single build cycle
--------------------

For a single build cycle, we implement:

* :meth:`make_components() <Assembly.make_components>` to return a
  :class:`dict` with :class:`Component` values.
* :meth:`make_constraints() <Assembly.make_constraints>` to return a
  :class:`list` of :class:`Constraint <cqparts.constraints.Constraint>` isntances.
* :meth:`make_alterations() <Assembly.make_alterations>` to (optionally) make
  changes to components.

To illustrate let's make a plate with cylinder sticking out of it, with a hole
to fasten it. The hole will be in a configurable location.


Cylinder Part
^^^^^^^^^^^^^^^

.. testcode::

    import cadquery
    import cqparts
    from cqparts.params import *
    from cqparts.display import display
    from cqparts.constraints import Mate

    class Cylinder(cqparts.Part):
        diam = PositiveFloat(10, doc="cylinder's diameter")
        length = PositiveFloat(10, doc="cylinder's length")
        embed = PositiveFloat(2, doc="embedding distance")
        hole_diam = PositiveFloat(2.72, doc="pilot hole diam")

        def make_base_cylinder(self):
            # This is used as a basis for make() and cutaway()
            return cadquery.Workplane('XY', origin=(0,0,-self.embed)) \
                .circle(self.diam/2).extrude(self.embed + self.length)

        def make(self):
            # Use the base cylindrical shape, and cut a hole through it
            return self.make_base_cylinder() \
                .faces(">Z").hole(self.hole_diam / 2)

        @property
        def cutaway(self):
            # Use the base cylindrical shape, no alterations
            return self.make_base_cylinder()

::

    display(Cylinder())

.. todo::

    display(Cylinder())


Plate Part
^^^^^^^^^^^^^^^

.. testcode::

    class Plate(cqparts.Part):
        length = PositiveFloat(100, doc="plate length")
        width = PositiveFloat(100, doc="plate width")
        thickness = PositiveFloat(10, doc="plate thickness")
        hole_offset = Float(50, doc="hole's offset from plate center along x-axis")
        hole_diam = PositiveFloat(3, doc="hole diameter")

        def make(self):
            return cadquery.Workplane('XY') \
                .box(self.length, self.width, self.thickness) \
                .moveTo(self.hole_offset, 0).hole(self.hole_diam)

        @property
        def mate_hole(self):
            return Mate((self.hole_offset, 0, self.thickness/2))

::

    display(Plate())

.. todo::

    display(Plate())


Demo Assembly
^^^^^^^^^^^^^^^^^^^^

And finally, lets combine the two to fully utilise a single build cycle.

.. testcode::

    from cqparts.constraints import LockConstraint, RelativeLockConstraint

    class Thing(cqparts.Assembly):

        def make_components(self):
            return {
                'pla': Plate(),
                'cyl': Cylinder(),
            }

        def make_constraints(self):
            return [
                LockConstraint(
                    component=self.components['pla'],
                    mate=Mate(origin=(-33,92,28), xDir=(1,0.5,0))  # a bit of random placement
                ),
                RelativeLockConstraint(
                    component=self.components['cyl'],
                    mate=self.components['pla'].mate_hole,
                    relative_to=self.components['pla']
                ),
            ]

        def make_alterations(self):
            # get Cylinder's location relative to the Plate
            coords = self.components['cyl'].world_coords - self.components['pla'].world_coords
            # apply that to the "cutout" we want to subtract from the plate
            cutout = coords + self.components['cyl'].cutout
            self.components['pla'].local_obj = self.components['pla'].local_obj.cut(cutout)

Now we end up with::

    thing = Thing()
    display(thing)

.. todo::

    display(thing)

But more importantly, the plate's geometry now looks like::

    display(thing.find('pla'))

.. todo::

    display(thing.find('pla'))


.. _parts_assembly-build-cycle_multiple:

Multiple build cycles
---------------------------
