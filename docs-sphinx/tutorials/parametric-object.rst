
.. _tutorials_parametricobject:

.. currentmodule:: cqparts.params


Parametric Object
==================

The *parametric object* is a fundamental part of the ``cqparts`` library.

:class:`ParametricObject` is a class to be (indirectly) inherited by your classes,
it uses :class:`Parameter` instances defined in the class to make assigning
class parameters transparent, and easy.

Although, for those of you well versed with Python, they may confuse you instead.


Create a Parametric Object
--------------------------

Let's create some :class:`ParametricObject` classes that use :class:`Parameter`.


Basic
^^^^^

.. doctest::

    >>> from cqparts.params import ParametricObject, Float, Int

    >>> class Thing(ParametricObject):
    ...     a = Float(10)
    ...     b = Int(20)

    >>> thing1 = Thing()
    >>> (thing1.a, thing1.b)
    (10.0, 20)

    >>> thing2 = Thing(a=1, b=-5)
    >>> (thing2.a, thing2.b)
    (1.0, -5)

In the above code ``Thing`` is a :class:`ParametricObject`, with
:class:`Parameter` instances defined in the class.

The ``a`` and ``b`` attributes are set as :class:`Float` and :class:`Int`
respectively, both of which are :class:`Parameter` classes.

When we instantiate a ``Thing``, everything passed in the constructor is
verified, and assigned to the instance as the given type.


Inherited Parameters
^^^^^^^^^^^^^^^^^^^^

Let's use ``Thing`` as a base type for another object we'll call ``Foo``.

.. doctest::

    >>> from cqparts.params import (
    ...     ParametricObject, Float, Int, Boolean
    ... )

    >>> class Thing(ParametricObject):
    ...     a = Float(10)
    ...     b = Int(20)

    >>> class Foo(Thing):
    ...     a = Float(None)
    ...     c = Boolean(False)

    >>> f = Foo(c=123)
    >>> (f.a, f.b, f.c)
    (None, 20, True)

Here you can notice:

* ``a`` was replaced by another :class:`Float`, with the default value changed.
* ``a``'s value is "nullable", which is true for most parameter types.
* ``b`` attribute was inherited from ``Thing``.
* ``c`` was added as a :class:`Boolean` parameter.
* ``c``'s value was cast from ``123`` to a :class:`bool`.


Initializing Parameters
^^^^^^^^^^^^^^^^^^^^^^^

Sometimes parameters need to be aware of each other's value so an instance can
initialize correctly, and be fully verified before continuing.

This is when :meth:`initialize_parameters <ParametricObject.initialize_parameters>`
can be utilised.

In the following example, the ``Bar`` class parameter ``foo`` will be prefixed
with "> " if the ``stuff`` parameter is >= 10.

.. doctest::

    >>> from cqparts.params import ParametricObject, PositiveInt, UpperCaseString

    >>> class Bar(ParametricObject):
    ...     stuff = PositiveInt(5)
    ...     foo = UpperCaseString('ABC')
    ...
    ...     def initialize_parameters(self):
    ...         if self.stuff >= 10:
    ...             self.foo = "> %s" % self.foo

    >>> Bar(foo='xyz').foo
    'XYZ'
    >>> Bar(stuff=20).foo
    '> ABC'


Mixing with Non-Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

Through the magic of Python you can use a :class:`ParametricObject` with non
:class:`Parameter` instances as well.

Just remember to call super's ``__init__`` like so.

.. doctest::

    >>> from cqparts.params import ParametricObject, Int

    >>> class Roo(ParametricObject):
    ...     a = Int(100)
    ...     b = 'beep beep like a sheep'
    ...
    ...     def __init__(self, c=10, **kwargs):
    ...         self.c = c
    ...         # alternatively: self.c = kwargs.pop('c', 10)
    ...         super(Roo, self).__init__(**kwargs)
    ...
    ...     @property
    ...     def abc(self):
    ...         return (self.a, self.b, self.c)

    >>> Roo(a=1, c=5).abc
    (1, 'beep beep like a sheep', 5)
    >>> Roo(b='abc')  # only Parameter types work # doctest: +SKIP
    ParameterError: <class 'Roo'> does not accept parameter(s): b


Builtin Parameters
------------------

:mod:`cqparts.params` has a number of :class:`Parameter` types, many have some
form of verification, and most are "nullable", meaning they can be validly set
to ``None``.


Parameter Verification
^^^^^^^^^^^^^^^^^^^^^^

Different :class:`Parameter` types don't just provide type casting, but
verification.

One example of this is the :class:`PositiveFloat` parameter type.

.. doctest::

    >>> from cqparts.params import ParametricObject, PositiveFloat

    >>> class Blah(ParametricObject):
    ...     width = PositiveFloat(10)

    >>> Blah(width=-6) # doctest: +SKIP
    ParameterError: value is not positive: -6


Create a Custom Parameter
-------------------------

You can also create your own custom parameters, this can provide some very
intuitive parameter formats for your creations.


Mapped Value Example
^^^^^^^^^^^^^^^^^^^^

Let's create a simple parameter that maps a key string to an integer value.

.. doctest::

    >>> from cqparts.params import Parameter, ParametricObject
    >>> from cqparts.errors import ParameterError

    >>> class SizeWord(Parameter):
    ...     def type(self, value):
    ...         try:
    ...             return {
    ...                 'tiny': 1,
    ...                 'small': 10,
    ...                 'large': 20,
    ...             }[value]
    ...         except KeyError:
    ...             raise ParameterError("invalid size: %r" % value)

    >>> class Flib(ParametricObject):
    ...     size = SizeWord('small')  # note: default is in string form

    >>> Flib().size
    10
    >>> Flib(size='tiny').size
    1
    >>> Flib(size='blah') # doctest: +SKIP
    ParameterError: invalid size: 'blah'


With ``@as_parameter``
^^^^^^^^^^^^^^^^^^^^^^^

One obvious use-case for a *parameter* is to pass parameter values to a container
class, sort of like a :class:`dict` that uses *attributes* as opposed to *items*.

You can do this with a single class using the :meth:`as_parameter` decorator.

.. doctest::

    >>> from cqparts.params import as_parameter, ParametricObject

    >>> @as_parameter(nullable=True)
    ... class Stuff(object):
    ...     def __init__(self, a=1, b=2, c=3):
    ...         self.a = a
    ...         self.b = b
    ...         self.c = c
    ...     @property
    ...     def abc(self):
    ...         return (self.a, self.b, self.c)

    >>> class Thing(ParametricObject):
    ...     foo = Stuff({'a': 10, 'b': 100}, doc="controls stuff")

    >>> thing = Thing(foo={'a': 20})
    >>> thing.foo.a
    20
    >>> thing.foo.abc
    (20, 2, 3)

.. warning::

    This method is mostly to save space, and to make the code read a bit more fluently.

    It has some limitations, and may cause more problems than it saves if
    you're not willing to dig into the code.


Documenting with Sphinx
-----------------------

The ``cqparts`` documentation is built using *shpinx* and *sphinx-autodoc*.

(see the link in this page's footer)

If you would like your parts to also use *sphinx*, then add ``_doc_type``
and ``doc`` to your *parameters* and *parametric objects* (respectively).

.. doctest::

    >>> from cqparts.params import *

    >>> class Thing(Parameter):
    ...     _doc_type = ':class:`float`'  # the type(value) past to the constructor

    >>> class Foo(ParametricObject):
    ...     width = Thing(123, doc="width of the base")


Also read up on the :mod:`cqparts.utils.sphinx` submodule.
