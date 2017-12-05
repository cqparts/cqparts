
.. _tutorial_assembly:

.. currentmodule:: cqparts.part

Make your own ``Assembly``
==========================

An :class:`Assembly` is a container for 1 to many :class:`Part` and/or
nested :class:`Assembly` instances.

Today we're going to make a toy car, and put it into an assembly.

This tutorial assumes you've been through the :ref:`tutorial_part` tutorial.

.. todo:: image of finished car assembly

Its structure will look something like this::

    car
     ├─○ chassis
     ├── front_axle
     │   ├─○ axle
     │   ├─○ left_wheel
     │   └─○ right_wheel
     └── rear_axle
         ├─○ axle
         ├─○ left_wheel
         └─○ right_wheel

Parts
------

For this *assembly* we're going to need the following *parts*

* **axle** : a simple long thin cylinder
* **wheel** : another simple cylinder
* **chassis** : an extruded :meth:`cadquery.Workplane.polyline`

While making these parts, we're going to design them based on how we want to
use them, but also on how others may want to use them.

Wheel
^^^^^^^^^^^^

The wheel's origin will be the point it meets the axle.

.. testcode::

    import cadquery
    import cqparts
    from cqparts.params import *
    from cqparts.display import render_props, display
    from cqparts.constraints import Mate

    class Wheel(cqparts.Part):
        # Parameters
        width = PositiveFloat(10, doc="width of wheel")
        diameter = PositiveFloat(30, doc="wheel diameter")

        # default appearance
        _render = render_props(template='wood_dark')

        def make(self):
            wheel = cadquery.Workplane('XY') \
                .circle(self.diameter / 2).extrude(self.width)
            return wheel

**Result**

::

    wheel = Wheel()
    display(wheel)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/toy-car/wheel.html"
        height="300px" width="100%"
    ></iframe>


Axle
^^^^^^^^^^^^

The vehicle's axle is a cylinder with a ``diameter`` and ``length``.

.. testcode::

    class Axle(cqparts.Part):
        # Parameters
        length = PositiveFloat(50, doc="axle length")
        diameter = PositiveFloat(10, doc="axle diameter")

        # default appearance
        _render = render_props(color=(50, 50, 50))  # dark grey

        def make(self):
            return cadquery.Workplane('ZX', origin=(0, -self.length/2, 0)) \
                .circle(self.diameter / 2).extrude(self.length)

        # axle's mates: assuming the wheels rotate around their z-axis
        @property
        def mate_left(self):
            return Mate(
                origin=(0, -self.length / 2, 0),
                xDir=(1, 0, 0), normal=(0, -1, 0),
            )

        @property
        def mate_right(self):
            return Mate(
                origin=(0, self.length / 2, 0),
                xDir=(1, 0, 0), normal=(0, 1, 0),
            )


We could have simply drawn a circle and extrude it, right?

The problem with that design is its implementation will involve
translating it by :math:`\frac{length}{2}`, and rotating :math:`90°` so
the :math:`Z` axis is along the world :math:`Y` axis.

Although that would not be difficult to do, it *is* messy.

Instead we've aligned the axle along the :math:`Y` axis, with the origin at the
cylinder's center, implemented in the ``make()`` function above.

**Mates**

A :class:`Mate <cqparts.constraints.mate.Mate>` is a relative *coordinate system*
used to connect *parts* in an *assembly*. We'll see how that works when we make
our first *assembly* later in this tutorial.

When assembling an axle we'll want to attach a wheel to each end. They're defined
above as ``mate_left`` and ``mate_right``.

Note that the ``normal`` for a :class:`Mate <cqparts.constraints.mate.Mate>`
is ``(0, 0, 1)`` by default :math:`+Z` axis. Changing this to the :math:`\pm Y`
axis for left/right rotates the wheel so that wheel's :math:`+Z` axis is
aligned accordingly.

**Result**

::

    axle = Axle()
    display(axle)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/toy-car/axle.html"
        height="300px" width="100%"
    ></iframe>


Chassis
^^^^^^^^^^^^

The chassis is a relatively complex shape that could have many
parameters. For the sake of simplicity in this tutorial, we're going to make
it a static face using :meth:`polyline() <cadquery.Workplane.polyline>` with a
variable :meth:`extrude() <cadquery.Workplane.extrude>` width.

.. testcode::

    class Chassis(cqparts.Part):
        # Parameters
        width = PositiveFloat(50, doc="chassis width")

        _render = render_props(template='wood_light')

        def make(self):
            points = [  # chassis outline
                (-60,0),(-60,22),(-47,23),(-37,40),
                (5,40),(23,25),(60,22),(60,0),
            ]
            return cadquery.Workplane('XZ', origin=(0,-self.width/2,0)) \
                .moveTo(*points[0]).polyline(points[1:]).close() \
                .extrude(self.width)

**Result**

::

    chassis = Chassis()
    display(chassis)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/toy-car/chassis.html"
        height="300px" width="100%"
    ></iframe>


Wheel Assembly
--------------------

We finally have all the parts we'll need, let's make our first *assembly*.

.. testcode::

    from cqparts.constraints import LockConstraint, RelativeLockConstraint

    class WheeledAxle(cqparts.Assembly):
        left_width = PositiveFloat(7, doc="left wheel width")
        right_width = PositiveFloat(7, doc="right wheel width")
        left_diam = PositiveFloat(25, doc="left wheel diameter")
        right_diam = PositiveFloat(25, doc="right wheel diameter")
        axle_diam = PositiveFloat(8, doc="axel diameter")
        axle_track = PositiveFloat(50, doc="distance between wheel tread midlines")

        def make_components(self):
            axel_length = self.axle_track - (self.left_width + self.right_width) / 2
            return {
                'axle': Axle(length=axel_length, diameter=self.axle_diam),
                'left_wheel': Wheel(
                     width=self.left_width, diameter=self.left_diam,
                ),
                'right_wheel': Wheel(
                     width=self.right_width, diameter=self.right_diam,
                ),
            }

        def make_constraints(self):
            return [
                LockConstraint(self.components['axle'], Mate()),
                RelativeLockConstraint(
                    self.components['left_wheel'],
                    self.components['axle'].mate_left,
                    self.components['axle']
                ),
                RelativeLockConstraint(
                    self.components['right_wheel'],
                    self.components['axle'].mate_right,
                    self.components['axle']
                ),
            ]

**Parameters**

Just like a :class:`Part`, the :class:`Assembly` class makes use of *parameters*.

These parameters can be passed directly or indirectly to *sub-assemblies*, or
to child *parts*. Note how ``axel_track`` is used to define the axle's length.

**Components**

The :meth:`Assembly.make_components` method is overridden above, to return
a :class:`dict` of named :class:`Component` instances.

Each component requires a name that's unique for the particular *assembly*.

*Components* may be added, or omitted based on the *assembly's* parameters
if necessary.

**Constraints**

The :meth:`Assembly.make_constraints` method is overridden to return a
:class:`list` of :meth:`Constraint <cqparts.constraints.Constraint>` instances.

Each *constraint* references, at least:

* the *component* being constrained.
* parameter(s) defining *how* it is to be constrained.

see :ref:`parts.constraints` for more details.

**Result**

::

    # wheels made asymmetrical to show that the
    # 2 wheels are independently created.
    wheeled_axle = WheeledAxle(right_width=2)
    display(wheeled_axle)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/toy-car/wheel-assembly.html"
        height="300px" width="100%"
    ></iframe>


Car Assembly
------------------


.. testcode::

    class Car(cqparts.Assembly):
        # Parameters
        wheelbase = PositiveFloat(70, "distance between front and rear axles")
        axle_track = PositiveFloat(60, "distance between tread midlines")
        # wheels
        front_wheel_width = PositiveFloat(10, doc="width of front wheels")
        rear_wheel_width = PositiveFloat(10, doc="width of rear wheels")
        front_wheel_diam = PositiveFloat(30, doc="front wheel diameter")
        rear_wheel_diam = PositiveFloat(30, doc="rear wheel diameter")
        axle_diam = PositiveFloat(10, doc="axle diameter")

        def make_components(self):
            pass

        def make_constraints(self):
            pass

.. todo::

    I'm getting to this...
