
Parts
=====

.. toctree::
   :caption: Contents:

   fasteners/index


.. _part_vs_assembly:

Part vs Assembly
----------------

A :class:`Part` is an `atomic` component; it cannot be disassembled, and it
is typically made of a single material.

An :class:`Assembly` is a collection of :class:`Part` instances &/or
nested :class:`Assembly` instances. An :class:`Assembly` would typically hold
itself together, as an intermedite step of construction.

.. tip::

   :class:`Part` is to :class:`Assembly` as ``file`` is to ``folder``.

:class:`Part` is not to be confused with a *primative* (like a *cube*, *sphere*,
or *cylinder* to name a few), nor is it to be confused with constructive
geometry


Physical Analogies
^^^^^^^^^^^^^^^^^^

The following ad nauseum analogies are to help you figure out your design.

**Constructive Analogy**

If you were to make something from scratch, from raw materials, each
:class:`Part` is each individual object after material processing
(such as *forging*, *printing*, or *milling*, just to name a few).

Each :class:`Assembly` would be a component that has reached an intermediate
step of assembly. Such as a motor, or a PCB.
The final *thing* being constructed is also an :class:`Assembly`

**Destructive Analogy**

Or put another way, if you had a *thing* with you, and you pulled it apart as
much as possible

This may involve *unscrewing*, *prying apart*, *de-soldering*, just to name a few.

Each time you pull out a *smaller thing*, if it *can* be disassembled further,
that is an :class:`Assembly`. If it *cannot* be pulled apart, then it's a
:class:`Part`.

When you have recursively disassembled everything, you will only be left
with :class:`Part` objects.


Design
^^^^^^

A well designed :class:`Assembly`
