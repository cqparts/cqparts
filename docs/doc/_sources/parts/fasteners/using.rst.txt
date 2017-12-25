
.. _parts_fasteners_using:

.. currentmodule:: cqparts.fasteners.utils

``Fastener`` Build Cycle
================================

As stated in :ref:`parts_fasteners_what`, a
:class:`Fastener <cqparts.fasteners.Fastener>` is an
:class:`Assemly <cqparts.part.Assembly>`, so it's highly recommended you
understand :ref:`parts_assembly-build-cycle` before reading this section.

A *fastener* still uses the *assembly* build cycle, but abstracts it further
with the use of 3 utility classes:

* the :class:`Evaluator`,
* the :class:`Selector`, and
* the :class:`Applicator` classes.

.. note::

    Using *fasteners* as a tool is **not mandatory**.

    You can always achieve the same effects by picking a *bolt*, *screw*, or
    anything else as a part, and adding that to your assembly manually.

    The :class:`Fastener <cqparts.fasteners.Fastener>` class is intended to
    make building easier. If it's more trouble than it's worth for your
    *assembly*, don't use one.


Evaluator
------------------

An :class:`Evaluator` instance is an assessment of the workpieces affected by
the fastener being applied.

The most common evaluator is the :class:`VectorEvaluator` which evaluates which
parts will be effected (by eliminating the white-list of parts passed to it),
and how they will be effected.

An :class:`Evaluator` instance is required to instantiate a
:class:`Selector`, and an :class:`Applicator`.

There is very little gouverning the structure of an :class:`Evaluator`, only
that is is passed a list of :class:`Part <cqparts.part.Part>` instances, and
that the overridden :class:`perform_evaluation() <Evaluator.perform_evaluation>`
method is buffered in the :meth:`eval <Evaluator.eval>` attribute.


Selector
-------------

The :class:`Selector` is what chooses, or tunes a *part* to fit the situation
assessed by the :class:`Evaluator`.

For example, a *bolt* that is the perfect length, or a *screw* that has enough
thread to grip, but no so much as to stick out the other side.

A :class:`Selector` also chooses where the screw fits in the fastener assembly.


Applicator
-------------

The :class:`Applicator` makes alterations to existing parts to either:

* cut solids to clear a path for the fastener, or
* add to solids to create an anchor point for a fastener to hold on to.

.. note::

    The typical *assembly* build cycle may perform alterations on components
    within that assembly, however a *fastener* assembly will make alterations
    on *components* in its parent *assembly*.

    There's no problem with this, it's just noteworthy.

**Why doesn't the applicator place parts?**

It may seem logical for the :class:`Applicator` to choose where parts fit into
the :class:`Fastener <cqparts.fasteners.Fastener>` assembly.

Instead, the :class:`Selector` sets the part placement for 2 reasons:

* **convenience**: the placement of fasteners actually has a lot to do with which
  components were selected, so the :class:`Selector` already has all the information
  when the selection is made.
* **clarity**: a *fastener* component will always require placement, but the
  parent's components will not always need to be altered. The presense of an
  :class:`Applicator` means that parent components **will** be changed in the
  process of building a fastener.


Built Cycle
---------------

Putting all the above utilities together, a :class:`Fastener <cqparts.fasteners.Fastener>`
build cycle is outlined below. Please reference :ref:`parts_assembly-build-cycle`
if needed.

In the *fastener's* :meth:`make_components() <cqparts.part.Assembly.make_components>` call:

1. An ``evaluator`` is instantiated.
2. A ``selector`` is instantiated, given the ``evaluator``
3. The *selector* returns the *parts* that will be part of this *assembly*

In the *fastener's* :meth:`make_constraints() <cqparts.part.Assembly.make_constraints>` call:

4. The ``selector`` returns the *constraints* that set the part's placement.

Then as part of the *assembly's* normal build cycle:

5. :meth:`solve() <cqparts.part.Assembly.solve>` is run, setting component
   world coordinates.

And finally, in the *fastener's* :meth:`make_alterations() <cqparts.part.Assembly.make_alterations>` call:

6. The ``applicator`` is instantiated, given both the ``evaluator`` and the ``selector``.
7. The ``applicator`` will make alterations to the geometry of the parts
   passed to the evaluator (if necessary).
