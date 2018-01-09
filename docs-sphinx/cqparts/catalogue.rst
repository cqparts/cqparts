
.. _cqparts.catalogue:

.. currentmodule:: cqparts.catalogue

Catalogue
======================

A catalogue is a simple file-based database to store parametric combinations
for components.


Analogy
----------

If a :class:`Component <cqparts.Component>` is a *blueprint*, the *parameters*
of its inherited :class:`ParametricObject <cqparts.params.ParametricObject>`
are the *measurements*, or *metrics* corresponding to the *blueprint*.

A :class:`Catalogue` is an exhaustive list of all parameter combinations,
for the context of manufacture, or purchase.

Each catalogued item can also contain information about the item that
aren't necessarily in the *blueprint*. Such as *make*, *model*, and
*product code*, as well as ids for *compatible items*, and even calculated
metrics like *area* (from *length* and *width* parameters).


Storage
--------------

A catalogue is represented in a single ``json`` file, using :mod:`tinydb`
to read & write.

.. note::

    More cataloguing methods may exist in future, but at this time only
    :class:`JSONCatalogue` is implemented.


Usage
-------------

Let's create an empty :class:`JSONCatalogue`, and push some
:class:`Component <cqparts.Component>` instances into it.


Create a new Catalogue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's say you'd like to save your catalogue in the file::

    >>> filename = 'my_catalogue.json'

.. testsetup::

    # temporary file (for demonstration purposes)
    import tempfile
    filename = tempfile.mktemp()

Then create the empty database:

.. doctest::

    >>> # Instantiate Catalogue
    >>> from cqparts.catalogue import JSONCatalogue
    >>> catalogue = JSONCatalogue(filename)


Add items
^^^^^^^^^^^^^^^^

Now let's create a few :class:`Box <cqparts_misc.basic.primatives.Box>` parts,
of varying lengths, and add them to the ``catalogue``.

Using the :meth:`JSONCatalogue.add` method, we give each *box* a unique ``id``,
some ``criteria``, and of course the ``obj``
:class:`Box <cqparts_misc.basic.primatives.Box>` instance we'd like to add.

.. doctest::

    >>> from cqparts_misc.basic.primatives import Box

    >>> # Add a few items
    >>> for length in [10, 20, 30]:
    ...     name = "box_L%g" % length
    ...     box = Box(length=length)
    ...     index = catalogue.add(
    ...         id=name,
    ...         criteria={
    ...             'type': 'box',
    ...             'lengthcode': 'L%i' % int(length),
    ...         },
    ...         obj=box
    ...     )

At this point, we can close the file::

    >>> catalogue.close()

which will commit the data to disk, ready for another script to read the
catalogue to search and instantiate the recorded *items*.

For this tutorial, we'll leave it open though. If you ran the above
:meth:`close() <JSONCatalogue.close>` code, you can just re-open it with::

    >>> catalogue = JSONCatalogue(filename)


Searching items
^^^^^^^^^^^^^^^^^^^^

Now that we have items in our ``catalogue``, we can search them with
:meth:`search() <JSONCatalogue.search>`, and :meth:`find() <JSONCatalogue.find>`.

:meth:`find() <JSONCatalogue.find>` will search the *catalogue*, and assert that
1, and only 1 result is returned.  Otherwise an exception is raised.

.. doctest::

    >>> # Find
    >>> item = catalogue.get_query()
    >>> result = catalogue.find(item.id == 'box_L20')
    >>> result.keys()
    [u'obj', u'id', u'criteria']
    >>> result['obj']['params']['length']
    20.0

If you're less certain that your query will yield a single result,
:meth:`search() <JSONCatalogue.search>` will return a list of positively
matching *items*.

.. doctest::

    >>> # Search
    >>> item = catalogue.get_query()
    >>> results = catalogue.search(item.criteria.type == 'box')
    >>> len(results)  # all 3 boxes
    3

To learn more about a catalogue's content, you can see its contents quite
easily from the *items* table:

.. doctest::

    >>> len(catalogue.items.all())  # everything in the catalogue
    3
    >>> i = catalogue.items.all()[0]
    >>> i['obj']['params']['length']
    10.0
    >>> i['id']
    u'box_L10'

    >>> # from this we've learnt that we can search with:
    >>> item = catalogue.get_query()
    >>> result = catalogue.find(item.obj.params.length == 10)
    >>> result['obj']['params']['length']
    10.0
    >>> result['id']  # the same item we got earlier
    u'box_L10'

To learn more about searching, read the :mod:`tinydb` docs.


Deserialize items
^^^^^^^^^^^^^^^^^^^^

Once an *item* has been selected from a catalogue, it can be instantiated
by deserializing it:

.. doctest::

    >>> # Get our catalogued 20mm long box
    >>> result = catalogue.find(item.id == 'box_L20')

    >>> # Creating object
    >>> catalogue.deserialize_result(result)
    <Box: height=1.0, length=20.0, width=1.0>

To streamline things, we can also do all of this in one line with the
:meth:`get() <JSONCatalogue.get>` method"

.. doctest::

    >>> # Search and deserialize in one line
    >>> catalogue.get(item.obj.params.length > 25)
    <Box: height=1.0, length=30.0, width=1.0>

.. note::

    All searching is done by :mod:`tinydb`, so
    :meth:`search() <JSONCatalogue.search>`, :meth:`find() <JSONCatalogue.find>`
    and :meth:`get_query() <JSONCatalogue.get_query>` are simply pass-throughs
    to the underlying :class:`tinydb.TinyDB` instance in the ``db`` attribute
    of this class.

    Please read the :mod:`tinydb` documentation, and query the database
    directly with this classes ``db`` attribute.


Item database example
^^^^^^^^^^^^^^^^^^^^^^^^^

Each catalogue item is stored in an ``items`` table within the database.

The ``items`` *table* is stored as a list, one of the elements stored in the
above example may be stored like this::

    {
        'id': 'box_L20',
        'criteria': {'lengthcode': 'L20', 'type': 'box'},
        'obj': {
            'class': {
                'module': 'cqparts_misc.basic.primatives',
                'name': 'Box',
            },
            'lib': {
                'name': 'cqparts',
                'version': '0.1.0',
            },
            'params': {
                '_render': {'alpha': 1.0, 'color': [192, 192, 192]},
                '_simple': False,
                'height': 1.0,
                'length': 20.0,
                'width': 1.0,
            }
        }
    }


.. testcleanup::

    # cleanup temporary file
    import os
    os.unlink(filename)
