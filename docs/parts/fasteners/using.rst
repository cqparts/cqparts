
.. _parts_fasteners_using:

.. currentmodule:: cqparts.fasteners.utils

Using Fasteners
===============

The :mod:`cqparts.fasteners` collection has some utilities to automatically apply and select
an apropriate fastener. What they do, and how to use them is documented below.

Using these tools is **not mandatory**; you'll always have the option to
explicitly select your fastener with the placement and orientation of your
choosing.


Evaluation
----------

An :class:`Evaluator` instance is an assessment of the workpieces intended to
be fastened along a given vector.

An :class:`Evaluator` instance is required for a
:class:`Selector`, and an :class:`Applicator`.

If a fastener :class:`Selector` is used to find an appropriate fastener, that
same :class:`Evaluator` instance can be passed to the :class:`Applicator`.

Evaluations are given, the *what*, and the *where*:

  * *what*: list of parts (those that may be effected, should be as short as possible)
  * *where*: linear edge, a vector along which the fastener is intended to be applied

A successful evaluation will yield:

  * list of parts effected (in order)
  * start & finish points on each effected part
    (the start being closer to the head)

There are 2 methods of evaluation

  * vector : faster, but may miss something
  * cylindrical : slower, but will find all interfacing solids


::

    # TODO: sample eval code


Selection
---------

An evaluation can be used to determine which fastener you need.
Or simply, how long the thread on your chosen fastener needs to be.

::

  # TODO: sample selector code


Application
-----------

So you have the fastener to apply, and the workpieces to attach, the workpieces
just need holes.

::

    from cqparts.search import find
    screw = find('10g_30mm_CS_PHIL')()
    # TODO:
    box = Box()  # FIXME
    plate = Plate()  # FIXME
    screw.apply()
