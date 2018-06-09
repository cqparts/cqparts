
.. currentmodule:: cqparts

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
  :class:`list` of :class:`Constraint <cqparts.constraint.Constraint>` isntances.
* :meth:`make_alterations() <Assembly.make_alterations>` to (optionally) make
  changes to components.

To illustrate let's make a plate with cylinder sticking out of it.
The plate will have a hole to fasten the cylinder.
The hole will be in a configurable location, and mounted at an angle.


Cylinder Part
^^^^^^^^^^^^^^^

.. testcode::

    import cadquery
    import cqparts
    from cqparts.params import *
    from cqparts.display import display, render_props
    from cqparts.utils.geometry import CoordSystem
    from cqparts.constraint import Mate

    class Cylinder(cqparts.Part):
        diam = PositiveFloat(10, doc="cylinder's diameter")
        length = PositiveFloat(10, doc="cylinder's length")
        embed = PositiveFloat(2, doc="embedding distance")
        hole_diam = PositiveFloat(2.72, doc="pilot hole diam")

        _render = render_props(alpha=0.8)

        def make_base_cylinder(self):
            # This is used as a basis for make() and cutaway()
            return cadquery.Workplane('XY') \
                .circle(self.diam/2).extrude(self.embed + self.length)

        def make(self):
            # Use the base cylindrical shape, and cut a hole through it
            return self.make_base_cylinder() \
                .faces(">Z").hole(self.hole_diam / 2)

        @property
        def cutaway(self):
            # Use the base cylindrical shape, no alterations
            return self.make_base_cylinder()

        @property
        def mate_embedded(self):
            return Mate(self, CoordSystem((0, 0, self.embed)))

::

    display(Cylinder())

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/asm-build-cycle/cylinder.html"
        height="300px" width="100%"
    ></iframe>


Plate Part
^^^^^^^^^^^^^^^

.. testcode::

    from math import sin, cos, radians

    class Plate(cqparts.Part):
        length = PositiveFloat(20, doc="plate length")
        width = PositiveFloat(20, doc="plate width")
        thickness = PositiveFloat(10, doc="plate thickness")
        hole_diam = PositiveFloat(3, doc="hole diameter")
        connection_offset = Float(4, doc="hole's offset from plate center along x-axis")
        connection_angle = Float(15, doc="angle of mate point")

        def make(self):
            plate = cadquery.Workplane('XY') \
                .box(self.length, self.width, self.thickness)
            hole_tool = cadquery.Workplane('XY', origin=(0, 0, -self.thickness * 5)) \
                .circle(self.hole_diam / 2).extrude(self.thickness * 10)
            hole_tool = self.mate_hole.local_coords + hole_tool
            return plate.cut(hole_tool)

        @property
        def mate_hole(self):
            return Mate(self, CoordSystem(
                origin=(self.connection_offset, 0, self.thickness/2),
                xDir=(1, 0, 0),
                normal=(0, -sin(radians(self.connection_angle)), cos(radians(self.connection_angle))),
            ))

Note that the hole through the plate is at an angle (by default :math:`15°`)

::

    display(Plate())

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/asm-build-cycle/plate.html"
        height="300px" width="100%"
    ></iframe>


Demo Assembly
^^^^^^^^^^^^^^^^^^^^

And finally, lets combine the two to fully utilise a single build cycle.

.. testcode::

    from cqparts.constraint import Fixed, Coincident

    class Thing(cqparts.Assembly):

        # Components are updated to self.components first
        def make_components(self):
            return {
                'pla': Plate(),
                'cyl': Cylinder(),
            }

        # Then constraints are appended to self.constraints (second)
        def make_constraints(self):
            plate = self.components['pla']
            cylinder = self.components['cyl']
            return [
                Fixed(
                    mate=plate.mate_origin,
                    world_coords=CoordSystem(origin=(-1,-5,-2), xDir=(-0.5,1,0))  # a bit of random placement
                ),
                Coincident(
                    mate=cylinder.mate_embedded,
                    to_mate=plate.mate_hole,
                ),
            ]

        # In between updating components, and adding constraints:
        #   self.solve() is run.
        # This gives each component a valid world_coords value, so
        # we can use it in the next step...

        # Lastly, this function is run (any return is ignored)
        def make_alterations(self):
            # get Cylinder's location relative to the Plate
            coords = self.components['cyl'].world_coords - self.components['pla'].world_coords
            # apply that to the "cutout" we want to subtract from the plate
            cutout = coords + self.components['cyl'].cutaway
            self.components['pla'].obj = self.components['pla'].obj.cut(cutout)

I got a bit lazy with the parameters there; ``Thing`` doesn't take any.

But in the end we get::

    thing = Thing()
    display(thing)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/asm-build-cycle/thing.html"
        height="300px" width="100%"
    ></iframe>

But more importantly, the plate's geometry now looks like this; displayed in
its local part coordinates::

    display(thing.find('pla'))

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/asm-build-cycle/plate-altered.html"
        height="300px" width="100%"
    ></iframe>

The ``Plate`` geometry is altered when used in the ``Thing`` :class:`Assembly`,
and the changes to ``Plate`` could be completely different if used in a different
:class:`Assembly`.

**But Why?**: Consider a builder constructing a wall, a *part* they may use is a length of
timber. During the wall's construction, the timber gets holes in it, from nails,
screws, bolts, or perhaps water pipes are threaded through. All of this detail
has **nothing** to do with the timber *part* before it's assembled. The alterations
to the length of timber is the onus of the *assembly*; the wall itself.


.. _parts_assembly-build-cycle_multiple:

Multiple build cycles
---------------------------

The cycles that make an *assembly* can be run multiple times in one build.

To do this, an assembly can return a generator using ``yield`` as opposed to
a ``return`` statement.

To demonstrate, let's replace the role of the
:class:`Coincident <cqparts.constraint.Coincident>`
by stacking some primative shapes using only
:class:`Fixed <cqparts.constraint.Fixed>` (a needless
restriction, but it serves as a good example).

To simplify things, we're going to use the :class:`Part` classes registered in
the :mod:`cqparts_misc.basic` module.

.. testcode::

    from cqparts_misc.basic.primatives import Cube, Box, Sphere

    class BlockStack(cqparts.Assembly):
        def make_components(self):
            print("make Box 'a'")
            yield {'a': Box(length=10, width=10, height=20)}  # grey

            print("make 2 Cubes 'b', and 'c'")
            yield {
                'b': Cube(size=8, _render={'color': (255, 0, 0)}),  # red
                'c': Cube(size=3, _render={'color': (0, 255, 0)}),  # green
            }

            print("make sphere 'd'")
            yield {'d': Sphere(radius=3, _render={'color': (0, 0, 255)})}  # blue

        def make_constraints(self):
            print("place 'a' at origin")
            a = self.components['a']
            yield [Fixed(a.mate_origin, CoordSystem((0,0,-10)))]

            print("place 'b' & 'c' relative to 'a'")
            b = self.components['b']
            c = self.components['c']
            yield [
                Fixed(b.mate_bottom, a.world_coords + a.mate_pos_x.local_coords),
                Fixed(c.mate_bottom, a.world_coords + a.mate_neg_y.local_coords),
            ]

            print("place sphere 'd' on cube 'b'")
            d = self.components['d']
            yield [Fixed(d.mate_origin, b.world_coords + b.mate_pos_x.local_coords)]

        def make_alterations(self):
            print("first round alteration(s)")
            yield
            print("second round alteration(s)")
            yield
            print("third round alteration(s)")
            yield

    block_stack = BlockStack()
    block_stack.build()

Note that in the 2nd and 3rd ``yield`` statements of ``make_constraints()``
we reference the ``.world_coords`` of some *components*. That's because
:meth:`solve() <Assembly.solve>` is run after each list of constraints is yielded.

When the assembly is built, we can see the print statements occur in the order:

.. testoutput::

    make Box 'a'
    place 'a' at origin
    first round alteration(s)
    make 2 Cubes 'b', and 'c'
    place 'b' & 'c' relative to 'a'
    second round alteration(s)
    make sphere 'd'
    place sphere 'd' on cube 'b'
    third round alteration(s)

And the final result::

    display(block_stack)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/asm-build-cycle/block_stack.html"
        height="300px" width="100%"
    ></iframe>
