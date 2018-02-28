
.. _cqparts_fasteners.index:

``cqparts_fasteners`` Module
====================================

**What is a Fastaner?**

A *fastener* is something that mechanically connects 2 or more *things* together,
such as a *screw*, *bolt*, or *nail*.

For us, a :class:`Fastener <cqparts_fasteners.Fastener>` is an
:class:`Assembly <cqparts.Assembly>` containing 1 or more
:class:`Part <cqparts.Part>` objects.

For example, a *nut* and *bolt* holidng together 2 parts together:

.. image:: /_static/img/fasteners.nut-and-bolt.01.png

may be in the hierarchy::

    thing
     ├○ part_a
     ├─ fastener
     │   ├○ bolt
     │   └○ nut
     └○ part_b


The ``cqparts_fasteners`` module contains:

* *parts* used as common *fastener* components (such as *nuts*, *bolts*, and *screws*)
* sub-parts for fastener components: :mod:`cqparts_fasteners.solidtypes`
* utility mechanisms to commonise how fasteners are applied to *assemblies*: :mod:`cqparts_fasteners.utils`


.. toctree::
   :caption: Contents

   build_cycle
   built-in/index
   easy-install/index
