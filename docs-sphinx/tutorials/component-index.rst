
.. _tutorial_component-index:

.. currentmodule:: cqparts.search

Component Index
===============

Any :class:`Component <cqparts.part.Component>` class can be added to the
``cqparts`` search index.

This will alow it to be found by other modules with concise code.

Registering, and searching is all done by the :mod:`cqparts.search` module.


Registering
-------------

Adding a :class:`Component <cqparts.part.Component>` to the search index is done
in one of 2 ways.


Decorator
^^^^^^^^^^

You can use the :meth:`register` method as a *class decorator*.

.. doctest::

    >>> import cqparts
    >>> from cqparts.params import *

    >>> @cqparts.search.register(a='one', b='two')
    ... class SomeThing(cqparts.Part):
    ...     length = Float(10)

    >>> @cqparts.search.register(a='one', b='three')
    ... class AnotherThing(cqparts.Assembly):
    ...     height = Int(100)

This has added thse two *components* to the ``cqparts`` search index.

Note that:

* ``SomeThing`` is a :class:`Part <cqparts.part.Part>`, and ``AnotherThing`` is an
  :class:`Assembly <cqparts.part.Assembly>`.
  It actually doesn't matter what they are, they will be added to the index, but
  they should be a :class:`Component <cqparts.part.Component>` of some sort.
* Both ``SomeThing`` and ``AnotherThing`` have a common criteria ``a='one'``

.. tip::

    Make your *component's* criteria **unique**.

    If it is not unique you run the risk of making yours, or other's
    *components* fail in searches.

    Possibly employ :meth:`common_criteria` to clean up your code.

Searching & Finding
---------------------

The 2 parts registered above can be found again with :meth:`search`::

    >>> from cqparts.search import search

    >>> search(a='one')
    {__main__.SomeThing, __main__.AnotherThing}

    >>> search(b='two', a='one')
    {__main__.SomeThing}

But most of the time you'll only be expecting one part to bounce back, because
mostly this is intended as an indexing tool, not a searching tool.

To index a unique part, or fail (throw an exception), use :meth:`find` instead::

    >>> from cqparts.search import find

    >>> find(a='one', b='two')
    __main__.SomeThing

    >>> # You can use this to build a component straight away
    >>> find(a='one', b='two')(length=50)  # creates an instance
    <SomeThing: length=50.0 @0x7fdfb28f4510>

This is great for uplling in a *component* with a registered *part number*.

Using :meth:`find` with criteria that is not unique will raise an exception::

    >>> find(a='one')
    SearchMultipleFoundError: 2 results found

Similarly, calling :meth:`find` with criteria that is not indexed will raise a
