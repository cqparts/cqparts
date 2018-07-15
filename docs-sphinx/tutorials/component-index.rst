
.. _tutorial_component-index:

.. currentmodule:: cqparts.search

Component Index
===============

Any :class:`Component <cqparts.Component>` class can be added to the
``cqparts`` search index, allowing it to be found by other modules with
concise code

This includes anything we've made in :ref:`tutorial_part` and
:ref:`tutorial_assembly`.

Registering, and searching is all done by the :mod:`cqparts.search` module.


Registering
-------------

Adding a :class:`Component <cqparts.Component>` to the search index is done
in one of 2 ways.


Decorator
^^^^^^^^^^

You can use the :meth:`register` method as a *class decorator*.

.. doctest::

    >>> import cqparts
    >>> from cqparts.search import register
    >>> from cqparts.params import *

    >>> @register(a='one', b='two')
    ... class SomeThing(cqparts.Part):
    ...     length = Float(10)

    >>> @register(a='one', b='three')
    ... class AnotherThing(cqparts.Assembly):
    ...     height = Int(100)

This has added thse two *components* to the ``cqparts`` search index.

Note that:

* ``SomeThing`` is a :class:`Part <cqparts.Part>`, and ``AnotherThing`` is an
  :class:`Assembly <cqparts.Assembly>`.
  It actually doesn't matter what they are, they will be added to the index, but
  they should be a :class:`Component <cqparts.Component>` of some sort.
* Both ``SomeThing`` and ``AnotherThing`` have a common criteria ``a='one'``

.. tip::

    Make your *component's* criteria **unique**.

    If it is not unique you run the risk of making yours, or other's
    *components* fail in searches.

    Possibly employ :meth:`common_criteria` to clean up your code.


Direct Register
^^^^^^^^^^^^^^^^

Components can also be registered by the :meth:`register` method without
using it as a decorator.

.. doctest::

    >>> import cqparts
    >>> from cqparts.search import register
    >>> from cqparts.params import *

    >>> class _SomeThing(cqparts.Part):
    ...     length = Float(10)
    >>> SomeThing = register(a='one', b='two')(_SomeThing)

    >>> class _AnotherThing(cqparts.Assembly):
    ...     height = Int(100)
    >>> AnotherThing = register(a='one', b='three')(_AnotherThing)

This and the decorated approach are functionally identical, which method you use
is dependent on your library's design, and which best suits you.


Searching & Finding
---------------------

The 2 parts registered above can be found again with :meth:`search` and/or :meth:`find`:


Search
^^^^^^^^^^

:meth:`search` returns a :class:`set` of all *components* that match the given
search criteria::

    >>> from cqparts.search import search

    >>> search(a='one')
    {__main__.SomeThing, __main__.AnotherThing}

    >>> search(b='two', a='one')
    {__main__.SomeThing}


Find
^^^^^^^^^^

But most of the time you'll only be expecting one part to bounce back, because
mostly this is intended as an indexing tool, not a searching tool.

To index a unique part, or fail (throw a
:class:`SearchError <cqparts.errors.SearchError>` exception), use :meth:`find`
instead::

    >>> from cqparts.search import find

    >>> find(a='one', b='two')
    __main__.SomeThing

    >>> # You can use this to build a component straight away
    >>> find(a='one', b='two')(length=50)  # creates an instance
    <SomeThing: length=50.0>

This is great for finding a *component* class with a registered *part number*.

Using :meth:`find` with criteria that is not unique will raise a
:class:`SearchMultipleFoundError <cqparts.errors.SearchMultipleFoundError>`
exception::

    >>> find(a='one')
    SearchMultipleFoundError: 2 results found

Similarly, calling :meth:`find` with criteria that is not indexed will raise a
:class:`SearchNoneFoundError <cqparts.errors.SearchNoneFoundError>`
exception::

    >>> find(b='infinity')
    SearchNoneFoundError: 0 results found
