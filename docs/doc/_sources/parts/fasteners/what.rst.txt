
.. _parts_fasteners_what:

What is a Fastener?
======================

A *fastener* is something that mechanically connects 2 or more *things* together,
such as a *screw*, *bolt*, or *nail*.

For us, a :class:`Fastener <cqparts.fasteners.Fastener>` is an
:class:`Assembly <cqparts.part.Assembly>` containing 1 or more
:class:`Part <cqparts.part.Part>` objects.

For example, a *nut* and *bolt* holidng together 2 parts together:

.. image:: /_static/img/fasteners.nut-and-bolt.01.png

may be in the hierarchy::

    thing
     ├○ part_a
     ├─ fastener
     │   ├○ bolt
     │   └○ nut
     └○ part_b

A *fastener* is also a convenient way to package relatively complex functionality
into more of a "point and shoot" implementation.
