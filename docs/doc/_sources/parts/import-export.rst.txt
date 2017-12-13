
.. _parts_import-export:

.. currentmodule:: cqparts.codec

Import / Export
===================

:class:`Part <cqparts.part.Part>` and :class:`Assembly <cqparts.part.Assembly>`
instances can be exported to file, and created by importing from file.

For any of the importers or exporters below,

Getting an Exporter
-------------------------

An exporter will get an existing :class:`Part <cqparts.part.Part>` or
:class:`Assembly <cqparts.part.Assembly>` and write it to file.

An :class:`Exporter` can be instantiated from a :class:`Part <cqparts.part.Part>`
or :class:`Assembly <cqparts.part.Assembly>` instance with the use of
:meth:`exporter() <cqparts.part.Component.exporter>`.

For example, exporting a ``.json`` file may be done with:

.. doctest::

    >>> from cqparts.basic.primatives import Cube
    >>> cube = Cube(size=2)

    >>> json_exporter = cube.exporter('json')
    >>> json_exporter('my_cube.json')

    >>> # or in a single line
    >>> cube.exporter('json')('my_cube.json')

each :class:`Exporter` will have different ways to call it, and different
parameters.


Getting an Importer
------------------------

Importers create a new instance of a :class:`Part <cqparts.part.Part>` or
:class:`Assembly <cqparts.part.Assembly>` from the data in the file being
imported.

So an :class:`Importer` is instantiated from :class:`Part <cqparts.part.Part>`
or :class:`Assembly <cqparts.part.Assembly>` *class* (not an instance of that class).

For example, importing a ``.STEP`` file may be achieved with:

.. doctest::

    >>> from cqparts import Part

    >>> step_importer = Part.importer('step')
    >>> my_part = step_importer('my_file.step')  # doctest: +SKIP

    >>> # or in a single line
    >>> my_part = Part.importer('step')('my_file.step')  # doctest: +SKIP

each :class:`Importer` will have different ways to call it, and different
parameters.

To use a specific importer, please find it in the :mod:`cqparts.codec` module
and read its documentation; each one should have examples.


Formats
-----------

Formats are documented in their respective :class:`Importer` and
:class:`Exporter` classes.

To learn more, have a look at the :mod:`cqparts.codec`
module page.


Creating your own
---------------------

If you'd like to create your own :class:`Exporter` or :class:`Importer` class,
you can do it, and register it!

To learn more, look at the example code in
:meth:`register_exporter` and :meth:`register_importer`.
