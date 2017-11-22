
Fasteners
=========

.. toctree::
   :caption: Contents:

   builtin
   using
   heads
   screw-drives
   threads
   custom

Definition
----------

A fastener is something that mechanically connects 2 or more *things* together,
such as a screw, bolt, or nail.
For us, a :class:`cqparts.fasteners.Fastener` is an :class:`Assembly`
containing 1 or more :class:`Part` objects.

For example, nut and bolt with washers either side would be a single fastener
assembly with a hierarchy of::

   my_bolt_fastener
      ├─○ bolt
      ├─○ washer_head
      ├─○ washer_nut
      └─○ nut


where all of ``nut``, ``washer_head``, ``washer_nut`` & ``bolt`` are :class:`Part` instances.

Whereas something like a screw would just have::

   my_screw_fastener
      └─○ screw

Which seems like an unnecessary layer, but programatically it serves very well
to distinguish between parts that constitute a fastener, and which don't.


Creating a Fastener
-------------------

There are many ways to create a fastener, too many to document here, but
I'll try to cover the basics


Making your own Fastener
------------------------
