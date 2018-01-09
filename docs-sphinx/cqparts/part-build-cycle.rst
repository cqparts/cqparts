
.. _parts_part-build-cycle:

.. currentmodule:: cqparts


``Part`` Build Cycle
========================

A :class:`Part` is just a container for a :class:`cadquery.Workplane` instance.

So the "building" of a *part* is more to help placement in the world, and to
facilitate changes made to that object.

For more information on how to create solids as a :class:`cadquery.Workplane`,
read more in the :mod:`cadquery` documentation.

Instantiation
------------------

When a :class:`Part` is created, it initializes its parameters.

Most of the work here is done by its parent class
:class:`ParametricObject <cqparts.params.ParametricObject>`.

This is covered in detail in :ref:`tutorials_parametricobject`.

.. note::

    :meth:`make() <Part.make>` is **not** called when **instantiating** a *part*; it's
    called later.

.. testcode::

    import cadquery
    import cqparts
    from cqparts.params import *

    class Box(cqparts.Part):
        x = Int(10)
        def initialize_parameters(self):
            print('initializing parameters...')
            print('    x = %r' % self.x)

        def make(self):
            print('running make()...')
            return cadquery.Workplane('XY').box(self.x,10,10)

So then when we simply create an instance...

.. doctest::

    >>> box = Box(x=20)
    initializing parameters...
        x = 20


Getting ``local_obj``
------------------------

When a *part's* ``local_obj`` is requested, the instance's
:meth:`make() <Part.make>` result is returned.

Note that in the above test, the ``print`` statement in ``make()`` doesn't show.
However, when we request ``local_obj``...

.. doctest::

    >>> box = Box(x=15)
    initializing parameters...
        x = 15
    >>> obj1 = box.local_obj
    running make()...
    >>> obj2 = box.local_obj


However nothing is printed on the 2nd call. This is because the result is
buffered, so when ``local_obj`` is requested a second time, it is
not re-made.

Most uses of a :class:`Part` will get the local object by referencing
``local_obj``, but you can forcefully remake the object in 2 ways:

.. doctest::

    >>> box = Box()
    initializing parameters...
        x = 10
    >>> obj = box.local_obj
    running make()...

    >>> # 1) set local_obj to None
    >>> box.local_obj = None
    >>> obj = box.local_obj
    running make()...

    >>> # 2) call make() explicitly
    >>> obj = box.make()
    running make()...

However you shouldn't need to do this.


``world_coords`` and ``world_obj``
----------------------------------------------

If :meth:`world_coords <Component.world_coords>` has been set, getting
:meth:`world_obj <Part.world_obj>` will create a copy of
:meth:`local_obj <Part.local_obj>` that has been transformed to
:meth:`world_coords <Component.world_coords>`.

That is to say that it is translated, and rotated so the object's local
coordinates are equal to the world coordinates, relative to the object itself.

Let's re-define ``Box`` without those print statements...

.. testcode::

    from cqparts.utils.geometry import CoordSystem

    class Box(cqparts.Part):
        x = Int(10)
        def make(self):
            return cadquery.Workplane('XY').box(self.x,10,10)

Now let's create a box, then set its location in the world by
setting :meth:`world_coords <Component.world_coords>`.

.. doctest::

    >>> box = Box()
    >>> box.local_obj.val().BoundingBox().ymin
    -5.0

    >>> # world_obj is None when the part does not have its world_coords
    >>> box.world_obj is None
    True

    >>> # let's translate across the y-axis
    >>> box.world_coords = CoordSystem(origin=(0,20,0))

    >>> # Now world_obj exists, and has been translated
    >>> isinstance(box.world_obj, cadquery.Workplane)
    True
    >>> box.world_obj.val().BoundingBox().ymin
    15.0


Changing ``local_obj`` or ``world_coords``
--------------------------------------------------

If :meth:`local_obj <Part.local_obj>` or
:meth:`world_coords <Component.world_coords>` is changed,
:meth:`world_obj <Part.world_obj>` is reset.

Then when :meth:`world_obj <Part.world_obj>` is requested again,
:meth:`local_obj <Part.local_obj>` is copied and moved,
just as it is explained above.

So the obvious thing to do now is to drill a hole through the box... right?

.. doctest::

    >>> box = Box()
    >>> box.world_coords = CoordSystem(origin=(0,20,0))
    >>> len(box.world_obj.val().Faces())
    6
    >>> box.local_obj = box.local_obj.faces(">Z").hole(2)
    >>> len(box.world_obj.val().Faces())
    7

Note that we changed :meth:`local_obj <Part.local_obj>`, but we tested the number of faces on
:meth:`world_obj <Part.world_obj>`. So we can conclude from this that when any changes are
made to the :meth:`local_obj <Part.local_obj>`, the
:meth:`world_obj <Part.world_obj>` is re-created using :meth:`local_obj <Part.local_obj>`
as reference.

Let's try the same thing by changing :meth:`world_obj <Part.world_obj>`:

.. doctest::

    >>> box = Box()
    >>> box.world_coords = CoordSystem(origin=(0,20,0))
    >>> box.world_obj = box.world_obj.faces(">Z").hole(2) # doctest: +SKIP
    ValueError: can't set world_obj directly, set local_obj instead

We get an exception instead

.. warning::

    :meth:`world_obj <Part.world_obj>` cannot be changed directly, but it can be
    changed indirectly via :meth:`local_obj <Part.local_obj>`.

**But Why?**: This is to avoid bad practices that encourage accumulated errors; if
the part can only be modified in its native coordinates, there is no possibility
of accumulated numerical error.

.. note::

    Remember: when changing the :meth:`local_obj <Part.local_obj>`, if your
    alterations are based on world coordinates, you must convert back to the
    object's local coordinates before the changes will match your expectations.

    Also remember that the :meth:`world_obj <Part.world_obj>` is likely rotated
    to fit into an *assembly*, so using queries like
    :meth:`faces(">Z") <cadquery.CQ.faces>` (for example) may not give you
    the information you're expecting.
