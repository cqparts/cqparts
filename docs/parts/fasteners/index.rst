
Fasteners
=========

.. toctree::
   :caption: Contents:

   types
   heads
   screw-drives
   threads
   custom

Definition
----------

A fastener is something that mechanically connects 2 or more parts together,
such as a screw, bolt, or nail.
For us, a :class:`cqparts.fasteners.Fastener` is an :class:`Assembly`
containing 1 or more :class:`Part` objects.

For example, nut and bolt with washers either side would be a single fastener
assembly with a hierarchy of::

   my_bolt_fastener
      - bolt
      - washer1
      - washer2
      - nut

where all of ``nut``, ``washer1``, ``washer2`` & ``bolt`` are :class:`Part` instances.

Whereas something like a screw would just have::

   my_screw_fastener
      - screw

Which seems like an unnecessary layer, but programatically it serves very well
to distinguish between parts that constitute a fastener, and which don't.


Composition of a Fastener
-------------------------

In the above example of a `nut` & `bolt`, the bolt is a single :class:`Part`, even
though conceptually it's got a number of components.

This is because the `bolt` itself is atomic; it cannot be dissassembled.

.. note::
   If you're about to go into your shed and get a hacksaw to proove me wrong,
   please have a read of :ref:`part_vs_assembly`.
