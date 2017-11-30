
Parts
=====

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    fasteners/index
    constraints/index


.. _part_vs_assembly:

Part vs Assembly
----------------

.. currentmodule:: cqparts.part

A :class:`Part` is a :class:`Component`, and an :class:`Assembly` is a :class:`Component`.

A :class:`Part` is an *atomic* component; it cannot be disassembled, and it
is typically made of a single material.

An :class:`Assembly` is a collection of :class:`Components <Component>`.

An :class:`Assembly` would typically hold itself together, as an intermedite
step of construction.

.. tip::

   :class:`Part` is to :class:`Assembly` as ``file`` is to ``folder``.

:class:`Part` is not to be confused with a *primative* (like a *cube*, *sphere*,
or *cylinder* to name a few), nor is it to be confused with constructive
geometry

For a detailed example of a hierarchy, have a look at the
:ref:`example servo motor <examples_servo_hierarchy>`.


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

Or put another way...


**Destructive Analogy**

If you had a *thing* with you, and you pulled it apart as much as possible
(this may involve *unscrewing*, *prying apart*, *de-soldering*, just to name a few).

Each time you pull out a *smaller thing*:

* if it *can* be disassembled further, that is an :class:`Assembly`.
* if it *cannot* be pulled apart, then it's a :class:`Part`.

When you have recursively disassembled everything, you will only be left
with :class:`Part` objects.


**Exceptions to the rule**

Just like any other *rule*, there are exceptions:

For example, an *SD Card* has many components inside it, but since it can be
assumed that it won't be pulled apart, or need to be constructed, an *SD Card*
will most likely be represented by a single :class:`Part`.

Conversely, a *sticker* (like a branding sticker) cannot be disassembled.
But visually you may want its orientation to be recognisable, or
you just want it to render properly. This is where a :class:`Part` is limited,
because it can only be one color. So the *sticker* may be 2 :class:`Part`
instances in an :class:`Assembly`, one for the backing, and one for the text,
or logo.


Design
^^^^^^

A well designed :class:`Assembly` is something that can be used in others'
creations.

That sentiment does *not* only apply to the highest level :class:`Assembly`, but
also lower level :class:`Assembly` classes used to create the high level object.

Consider how others may want to use your :class:`Assembly`, and empower the
class with the tools necessary to make their job easy.

More discussion on this in :ref:`tutorial_assembly`.
