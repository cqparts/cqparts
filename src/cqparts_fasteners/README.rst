
=========================================
`cqparts` Content Library : Fasteners
=========================================

Components
-------------------------

**Base Components**

Few of these are useful on their own, they're used to build more complex parts.

Heads
^^^^^^^^^^^^^^^^^

* Counter-sunk varieties
* Cylindrical varieties
* Externally Driven (eg: hex head)

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/heads-assorted.png

Drive Types
^^^^^^^^^^^^^^^^^

* Cruciform varieties (eg: phillips, frearson)
* Hex (aka: alan) varieties
* Square varieties (eg: single, double, triple square)
* Slotted
* Tamper Resistant varieties

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/drives-assorted.png

Threads
^^^^^^^^^^^^^^^^^^

Standard threads included:

* ISO68 (standard for metric bolts)
* Triangular (eg: for woodscrews)
* Ball Screw

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/threads-assorted.png

Any custom thread can be built by creating a *profile* as a ``Wire`` from within
an object inheriting from the base ``Thread`` class.
(`read more here <https://fragmuffin.github.io/cqparts/doc/api/cqparts_fasteners.solidtypes.threads.html?highlight=build_profile#cqparts_fasteners.solidtypes.threads.base.Thread>`_)

.. note::

    Threads currently bugged by `issue #1 <https://github.com/fragmuffin/cqparts/issues/1>`_.

    Threads are currently simplified to a cylinder until this is fixed.

    Warning when using for 3d printing, threads will not form correctly until the
    bug is fixed... please ``+1`` the issue if you'd like to use properly formed
    threads.

Male Fastener Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bolts
* Screws

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/male-assorted.png

Female Fastener Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Nuts

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/female-assorted.png

Utilities
-------------------------

The ``Fasteners`` utility assembly can be used to automatically apply fasteners
to arbitrary materials.


For example, with the following 2 detatched blocks:

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/fastener-detatched.png

A ``Fastener`` can be applied to these two blocks to hold them together in a
variety of ways, with varied parameters, such as these 2 exmples:

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/fastener-assorted.png

More detailed examples of customizing a ``Fastener`` are
`documented here <https://fragmuffin.github.io/cqparts/doc/cqparts_fasteners/>`_.

.. image:: https://fragmuffin.github.io/cqparts/media/img/fasteners/fastener-custom-assorted.png


Catalogue(s)
-------------------------

**BoltDepot**

`boltdepot.com`_ has an exceptional website for details of their products, enough
to build 3d models accurate enough for most applications.

At this time, the catalogue you get with this library contains some of the
products for `boltdepot.com`_ in the categories:

* Bolts : ``boltdepot-bolts.json``
* Nuts : ``boltdepot-nuts.json``
* Woodscrews : ``boltdepot-woodscrews.json``

**Other Suppliers**

With increased interest in this library I would like to see this list grow, but
at this time, it's just the catalogues listed above.


Examples
-------------------------

``Screw``
^^^^^^^^^^^^^^^^^^^^^^^

TODO: code
TODO: image

Catalogue ``Bolt``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO: code
TODO: image
