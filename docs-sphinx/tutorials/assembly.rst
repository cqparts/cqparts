
.. _tutorial_assembly:

.. currentmodule:: cqparts.part

Make your own ``Assembly``
==========================

An :class:`Assembly` is a container for 1 to many :class:`Part` and/or
nested :class:`Assembly` instances.

Today we're going to make a toy car, and put it into an assembly.

This tutorial assumes you've been through the :ref:`tutorial_part` tutorial.

.. warning::

    TODO: image of finished assembly

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

Axle
^^^^^^^^^^^^

The vehicle's axle is a cylinder with a ``diameter`` and ``length``.
So we could simply draw a circle and extrude it, right?

The problem with this design is that it's implementation will involve
translating it by :math:`\frac{length}{2}`, and rotating :math:`90°` so
the :math:`Z` axis is along the world :math:`Y` axis.

Although that's not difficult, it is messy.

Instead we'll align the axle along the :math:`Y` axis, with the origin at the
cylinder's center. This can be seen in the ``make()`` function.

**Mates**

A :class:`Mate <cqparts.constraints.mate.Mate>` is a relative *coordinate system*
used to connect *parts* in an *assembly*.

For the axle we'll want to attach a wheel to each end, so they're defined
below as ``mate_left`` and ``mate_right``

.. testcode::

    import cadquery
    import cqparts
    from cqparts.params import *
    from cqparts.display import render_props, display
    from cqparts.constraints.mate import Mate

    class Axle(cqparts.Part):
        # Parameters
        length = PositiveFloat(50, doc="axle length")
        diameter = PositiveFloat(10, doc="axle diameter")

        # default appearance
        _render = render_props(color=(50, 50, 50))  # dark grey

        def make(self):
            return cadquery.Workplane('ZX', origin=(0, -self.length/2, 0)) \
                .circle(self.diameter / 2).extrude(self.length)

        @property
        def mate_left(self):
            return Mate((0, -self.length / 2, 0))

        @property
        def mate_right(self):
            return Mate((0, self.length / 2, 0))

::

    display(Axle())

.. image:: img/assembly.part-axle.png

Wheel
^^^^^^^^^^^^

The wheel's origin will be the point it meets the axle.

We'll build it on the left side by default, but if it's configured as a
right wheel, we'll :meth:`mirror() <cadquery.CQ.mirror>` its geometry
over the 'XZ' plane.

Note that a mirror is preferable to a :math:`180°` rotation because if an
asymetrical tread is introduced, a mirror would be more appropriate.

Also, so we can name the side as "left" and "right", we can make a parameter
that only accepts these 2 options.

.. testcode::

    class Side(NonNullParameter):
        def type(self, value):
            if not value in ('left', 'right'):
                raise ParameterError("must be 'left' or 'right'")
            return value

    class Wheel(cqparts.Part):
        # Parameters
        side = Side('left', doc="which side the wheel is on")
        width = PositiveFloat(10, doc="width of wheel")
        diameter = PositiveFloat(30, doc="wheel diameter")

        # default appearance
        _render = render_props(template='wood_dark')

        def make(self):
            wheel = cadquery.Workplane('XZ') \
                .circle(self.diameter / 2).extrude(self.width)
            if self.side == 'right':
                wheel = wheel.mirror('XZ')
            return wheel

::

    display(Wheel())

.. image:: img/assembly.part-wheel.png

Chassis
^^^^^^^^^^^^

The chassis is a relatively complex shape that could have many
parameters. For the sake of simplicity in this tutorial, we're going to make
it a static face using :meth:`polyline() <cadquery.Workplane.polyline>` with a
variable :meth:`extrude() <cadquery.Workplane.extrude>` width.

**Mates**

Mates will be necessary for the front and rear axles, these can be seen below as
``mate_axle_front`` and ``mate_axle_rear``.

.. testcode::

    class Chassis(cqparts.Part):
        # Parameters
        wheelbase = PositiveFloat(70, "distance between front and rear axles")



Wheel Assembly
--------------------

Car Assembly
------------------


.. testcode::

    class Car(cqparts.Assembly):
        # Parameters
        wheelbase = PositiveFloat(70, "distance between front and rear axles")
        axle_track = PositiveFloat(60, "distance between tread midlines")
        front_wheel_width = PositiveFloat(10, doc="width of front wheels")
        rear_wheel_width = PositiveFloat(10, doc="width of rear wheels")
        front_wheel_diam = PositiveFloat(30, doc="front wheel diameter")
        rear_wheel_diam = PositiveFloat(30, doc="rear wheel diameter")

        def make_components(self):
            pass

        def make_constraints(self):
            pass
