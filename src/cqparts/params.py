import six
from copy import copy
from importlib import import_module

from . import __version__
from .errors import ParameterError

import logging
log = logging.getLogger(__name__)


class ParametricObject(object):
    """
    Parametric objects may be defined like so:

    .. doctest::

        >>> from cqparts.params import (
        ...     ParametricObject,
        ...     PositiveFloat, IntRange,
        ... )

        >>> class Foo(ParametricObject):
        ...     x = PositiveFloat(5)
        ...     i = IntRange(1, 10, 3)  # between 1 and 10, defaults to 3
        ...     blah = 100

        >>> a = Foo(i=8)
        >>> (a.x, a.i)
        (5.0, 8)

        >>> a = Foo(i=11) # raises exception # doctest: +SKIP
        ParameterError: value of 11 outside the range {1, 10}

        >>> a = Foo(z=1)  # raises exception # doctest: +SKIP
        ParameterError: <class 'Foo'> does not accept parameter(s): z

        >>> a = Foo(x='123', i='2')
        >>> (a.x, a.i)
        (123.0, 2)

        >>> a = Foo(blah=200)  # raises exception, parameters must be Parameter types # doctest: +SKIP
        ParameterError: <class 'Foo'> does not accept any of the parameters: blah

        >>> a = Foo(x=None)  # a.x is None, a.i=3
        >>> (a.x, a.i)
        (None, 3)

    Internally to the object, parameters may be accessed simply with self.x, self.i
    These will always return the type defined

    """
    def __init__(self, **kwargs):
        # get all available parameters (recurse through inherited classes)
        params = self.class_params(hidden=True)

        # parameters explicitly defined during intantiation
        defined_params = set(kwargs.keys())

        # only accept a subset of params
        invalid_params = defined_params - set(params.keys())
        if invalid_params:
            raise ParameterError("{cls} does not accept parameter(s): {keys}".format(
                cls=repr(type(self)),
                keys=', '.join(sorted(invalid_params)),
            ))

        # Cast parameters into this instance
        for (name, param) in params.items():
            value = param.default
            if name in kwargs:
                value = param.cast(kwargs[name])
            setattr(self, name, value)

        self.initialize_parameters()

    @classmethod
    def class_param_names(cls, hidden=True):
        """
        Return the names of all class parameters.

        :param hidden: if ``False``, excludes parameters with a ``_`` prefix.
        :type hidden: :class:`bool`
        :return: set of parameter names
        :rtype: :class:`set`
        """
        param_names = set(
            k for (k, v) in cls.__dict__.items()
            if isinstance(v, Parameter)
        )
        for parent in cls.__bases__:
            if hasattr(parent, 'class_param_names'):
                param_names |= parent.class_param_names(hidden=hidden)

        if not hidden:
            param_names = set(n for n in param_names if not n.startswith('_'))
        return param_names

    @classmethod
    def class_params(cls, hidden=True):
        """
        Gets all class parameters, and their :class:`Parameter` instances.

        :return: dict of the form: ``{<name>: <Parameter instance>, ... }``
        :rtype: :class:`dict`

        .. note::

            The :class:`Parameter` instances returned do not have a value, only
            a default value.

            To get a list of an **instance's** parameters and values, use
            :meth:`params` instead.

        """
        param_names = cls.class_param_names(hidden=hidden)
        return dict(
            (name, getattr(cls, name))
            for name in param_names
        )

    def params(self, hidden=True):
        """
        Gets all instance parameters, and their *cast* values.

        :return: dict of the form: ``{<name>: <value>, ... }``
        :rtype: :class:`dict`
        """
        param_names = self.class_param_names(hidden=hidden)
        return dict(
            (name, getattr(self, name))
            for name in param_names
        )

    def __repr__(self):
        # Returns string of the form:
        #   <ClassName: diameter=3.0, height=2.0, twist=0.0>
        params = self.params(hidden=False)
        return "<{cls}: {params}>".format(
            cls=type(self).__name__,
            params=", ".join(
                "%s=%r" % (k, v)
                for (k, v) in sorted(params.items(), key=lambda x: x[0])  # sort by name
            ),
        )

    def initialize_parameters(self):
        """
        A palce to set default parameters more intelegently than just a
        simple default value (does nothing by default)

        :return: ``None``

        Executed just prior to exiting the :meth:`__init__` function.

        When overriding, strongly consider calling :meth:`super`.

        """
        pass

    # Serialize / Deserialize
    def serialize(self):
        """
        Encode a :class:`ParametricObject` instance to an object that can be
        encoded by the :mod:`json` module.

        :return: a dict of the format:
        :rtype: :class:`dict`

        ::

            {
                'lib': {  # library information
                    'name': 'cqparts',
                    'version': '0.1.0',
                },
                'class': {  # importable class
                    'module': 'yourpartslib.submodule',  # module containing class
                    'name': 'AwesomeThing',  # class being serialized
                },
                'params': {  # serialized parameters of AwesomeThing
                    'x': 10,
                    'y': 20,
                }
            }

        value of ``params`` key comes from :meth:`serialize_parameters`

        .. important::

            Serialize pulls the class name from the classes ``__name__`` parameter.

            This must be the same name of the object holding the class data, or
            the instance cannot be re-instantiated by :meth:`deserialize`.

        **Examples (good / bad)**

        .. doctest::

            >>> from cqparts.params import ParametricObject, Int

            >>> # GOOD Example
            >>> class A(ParametricObject):
            ...     x = Int(10)
            >>> A().serialize()['class']['name']
            'A'

            >>> # BAD Example
            >>> B = type('Foo', (ParametricObject,), {'x': Int(10)})
            >>> B().serialize()['class']['name']  # doctest: +SKIP
            'Foo'

        In the second example, the classes import name is expected to be ``B``.
        But instead, the *name* ``Foo`` is recorded. This missmatch will be
        irreconcilable when attempting to :meth:`deserialize`.
        """
        return {
            # Encode library information (future-proofing)
            'lib': {
                'name': 'cqparts',
                'version': __version__,
            },
            # class & name record, for automated import when decoding
            'class': {
                'module': type(self).__module__,
                'name': type(self).__name__,
            },
            'params': self.serialize_parameters(),
        }

    def serialize_parameters(self):
        """
        Get the parameter data in its serialized form.

        Data is serialized by each parameter's :meth:`Parameter.serialize`
        implementation.

        :return: serialized parameter data in the form: ``{<name>: <serial data>, ...}``
        :rtype: :class:`dict`
        """

        # Get parameter data
        class_params = self.class_params()
        instance_params = self.params()

        # Serialize each parameter
        serialized = {}
        for name in class_params.keys():
            param = class_params[name]
            value = instance_params[name]
            serialized[name] = param.serialize(value)
        return serialized

    @staticmethod
    def deserialize(data):
        """
        Create instance from serial data
        """
        # Import module & get class
        try:
            module = import_module(data['class']['module'])
            cls = getattr(module, data['class']['name'])
        except ImportError:
            raise ImportError("No module named: %r" % data['class']['module'])
        except AttributeError:
            raise ImportError("module %r does not contain class %r" % (
                data['class']['module'], data['class']['name']
            ))

        # Deserialize parameters
        class_params = cls.class_params(hidden=True)
        params = dict(
            (name, class_params[name].deserialize(value))
            for (name, value) in data['params'].items()
        )

        # Instantiate new instance
        return cls(**params)

    #@staticmethod
    #def deserialized_class(data):


# ========================  Parameter Types  ========================
class Parameter(object):
    """
    Used to set parameters of a :class:`ParametricObject`.

    All instances of this class defined in a class' ``__dict__`` will be
    valid input to the object's constructor.

    **Creating your own Parameter**

    To create your own parameter type, inherit from this class and override
    the :meth:`type` method.

    To demonstrate, let's create a parameter that takes an integer, and
    multiplies it by 10.

    .. doctest::

        >>> from cqparts.params import Parameter
        >>> class Tens(Parameter):
        ...     _doc_type = ":class:`int`"
        ...     def type(self, value):
        ...         return int(value) * 10

    Now to use it in a :class:`ParametricObject`

    .. doctest::

        >>> from cqparts.params import ParametricObject
        >>> class Foo(ParametricObject):
        ...     a = Tens(5, doc="a in groups of ten")
        ...     def bar(self):
        ...         print("a = %i" % self.a)

        >>> f = Foo(a=8)
        >>> f.bar()
        a = 80

    """

    def __init__(self, default=None, doc=None):
        """
        :param default: default value, will cast before storing
        """
        self.default = self.cast(default)
        self.doc = doc

    @classmethod
    def new(cls, default=None):
        """
        Create new instance of the parameter with a new default
        ``doc``

        :param default: new parameter instance default value
        """
        return cls(default=default)

    def cast(self, value):
        """
        First layer of type casting, used for high-level verification.

        If ``value`` is ``None``, :meth:`type` is not called to cast the value
        further.

        :param value: the value given to the :class:`ParametricObject`'s constructor
        :return: ``value`` or ``None``
        :raises ParameterError: if type is invalid
        """
        if value is None:
            return None
        return self.type(value)

    def type(self, value):
        """
        Second layer of type casting, usually overridden to change the given
        ``value`` into the parameter's type.

        Casts given value to the type dictated by this parameter type.

        Raise a :class:`ParameterError` on errors.

        :param value: the value given to the :class:`ParametricObject`'s constructor
        :return: ``value`` cast to parameter's type
        :raises ParameterError: if type is invalid
        """
        return value

    # sphinx documentation helpers
    def _param(self):
        # for a sphinx line:
        #   :param my_param: <return is published here>
        if not isinstance(self.doc, six.string_types):
            return "[no description]"
        return self.doc

    _doc_type = '[unknown]'

    def _type(self):
        # for a sphinx line:
        #   :type my_param: <return is published here>
        return self._doc_type

    # Serializing / Deserializing
    @classmethod
    def serialize(cls, value):
        r"""
        Converts value to something serializable by :mod:`json`.

        :param value: value to convert
        :return: :mod:`json` serializable equivalent

        By default, returns ``value``, to pass straight to :mod:`json`

        .. warning::

            :meth:`serialize` and :meth:`deserialize` **are not** symetrical.


        **Example of serializing then deserializing a custom object**

        Let's create our own ``Color`` class we'd like to represent as a
        parameter.

        .. doctest::

            >>> class Color(object):
            ...     def __init__(self, r, g, b):
            ...         self.r = r
            ...         self.g = g
            ...         self.b = b
            ...
            ...     def __eq__(self, other):
            ...         return (
            ...             type(self) == type(other) and \
            ...             self.r == other.r and \
            ...             self.g == other.g and \
            ...             self.b == other.b
            ...         )
            ...
            ...     def __repr__(self):
            ...         return "<Color: %i, %i, %i>" % (self.r, self.g, self.b)

            >>> from cqparts.params import Parameter
            >>> class ColorParam(Parameter):
            ...     _doc_type = ":class:`list`"  # for sphinx documentation
            ...     def type(self, value):
            ...         (r, g, b) = value
            ...         return Color(r, g, b)
            ...
            ...     @classmethod
            ...     def serialize(cls, value):
            ...         # the default serialize will fail, we know this
            ...         # because json.dumps(Color(0,0,0)) raises an exception
            ...         if value is None:  # parameter is nullable
            ...             return None
            ...         return [value.r, value.g, value.b]
            ...
            ...     @classmethod
            ...     def deserialize(cls, value):
            ...         # the de-serialized rgb list is good to pass to type
            ...         return value

        Note that ``json_deserialize`` does not return a ``Color`` instance.
        Intead, it returns a *list* to be used as an input to :meth:`cast`
        (which is ultimately passed to :meth:`type`)

        This is because when the values are deserialized, they're used as the
        default values for a newly created :class:`ParametricObject` class.

        So now when we use them in a :class:`ParametricObject`:

        .. doctest::

            >>> from cqparts.params import ParametricObject, Float
            >>> class MyObject(ParametricObject):
            ...     color = ColorParam(default=[127, 127, 127])  # default 50% grey
            ...     height = Float(10)

            >>> my_object = MyObject(color=[100, 200, 255])
            >>> my_object.color  # is a Color instance (not a list)
            <Color: 100, 200, 255>

        Now to demonstrate how a parameter goes in and out of being serialized,
        we'll create a ``test`` method that, doesn't do anything, except that
        it should *not* throw any exceptions from its assertions, or the call
        to :meth:`json.dumps`

        .. doctest::

            >>> import json

            >>> def test(value, obj_class=Color, param_class=ColorParam):
            ...     orig_obj = param_class().cast(value)
            ...
            ...     # serialize
            ...     if value is None:
            ...         assert orig_obj == None
            ...     else:
            ...         assert isinstance(orig_obj, obj_class)
            ...     serialized = json.dumps(param_class.serialize(orig_obj))
            ...
            ...     # show serialized value
            ...     print(serialized)  # as a json string
            ...
            ...     # deserialize
            ...     ds_value = param_class.deserialize(json.loads(serialized))
            ...     new_obj = param_class().cast(ds_value)
            ...
            ...     # now orig_obj and new_obj should be identical
            ...     assert orig_obj == new_obj
            ...     print("all good")

            >>> test([1, 2, 3])
            [1, 2, 3]
            all good
            >>> test(None)
            null
            all good

        These are used to serialize and deserialize :class:`ParametricObject`
        instances, so they may be added to a catalogue, then re-created.

        To learn more, go to :meth:`ParametricObject.serialize`

        """
        return value

    @classmethod
    def deserialize(cls, value):
        """
        Converts :mod:`json` deserialized value to its python equivalent.

        :param value: :mod:`json` deserialized value
        :return: python equivalent of ``value``

        .. important::

            ``value`` must be deserialized to be a valid input to :meth:`cast`

        More information on this in :meth:`serialize`

        """
        return value



# ------------ float types ---------------
class Float(Parameter):
    """
    Floating point
    """

    _doc_type = ':class:`float`'

    def type(self, value):
        try:
            cast_value = float(value)
        except ValueError:
            raise ParameterError("value cannot be cast to a float: %r" % value)
        return cast_value


class PositiveFloat(Float):
    """
    Floating point >= 0
    """
    def type(self, value):
        cast_value = super(PositiveFloat, self).type(value)
        if cast_value < 0:
            raise ParameterError("value is not positive: %g" % cast_value)
        return cast_value


class FloatRange(Float):
    """
    Floating point in the given range (inclusive)
    """
    def __init__(self, min, max, default, doc="[no description]"):
        """
        {``min`` <= value <= ``max``}

        :param min: minimum value
        :type min: float
        :param max: maximum value
        :type max: float
        """
        self.min = min
        self.max = max
        super(FloatRange, self).__init__(default, doc=doc)

    def type(self, value):
        cast_value = super(FloatRange, self).type(value)

        # Check range (min/max value of None is equivelant to -inf/inf)
        inside_range = True
        if (self.min is not None) and (cast_value < self.min):
            inside_range = False
        if (self.max is not None) and (cast_value > self.max):
            inside_range = False

        if not inside_range:
            raise ParameterError("value of %g outside the range {%s, %s}" % (
                cast_value, self.min, self.max
            ))

        return cast_value

# ------------ int types ---------------
class Int(Parameter):
    """
    Integer value
    """
    _doc_type = ":class:`int`"

    def type(self, value):
        try:
            cast_value = int(value)
        except ValueError:
            raise ParameterError("value cannot be cast to an integer: %r" % value)
        return cast_value


class PositiveInt(Int):
    """
    Integer >= 0
    """
    def type(self, value):
        cast_value = super(PositiveInt, self).type(value)
        if cast_value < 0:
            raise ParameterError("value is not positive: %g" % cast_value)
        return cast_value


class IntRange(Int):
    """
    Integer in the given range (inclusive)
    """
    def __init__(self, min, max, default, doc="[no description]"):
        """
        {``min`` <= value <= ``max``}

        :param min: minimum value
        :type min: int
        :param max: maximum value
        :type max: int
        """
        self.min = min
        self.max = max
        super(IntRange, self).__init__(default, doc=doc)

    def type(self, value):
        cast_value = super(IntRange, self).type(value)

        # Check range (min/max value of None is equivelant to -inf/inf)
        inside_range = True
        if (self.min is not None) and (cast_value < self.min):
            inside_range = False
        if (self.max is not None) and (cast_value > self.max):
            inside_range = False

        if not inside_range:
            raise ParameterError("value of %g outside the range {%s, %s}" % (
                cast_value, self.min, self.max
            ))

        return cast_value


# ------------ boolean types ------------
class Boolean(Parameter):
    """
    Boolean value
    """

    _doc_type = ':class:`bool`'

    def type(self, value):
        try:
            cast_value = bool(value)
        except ValueError:
            raise ParameterError("value cannot be cast to bool: %r" % value)
        return cast_value


# ------------ string types ------------
class String(Parameter):
    """
    String value
    """

    _doc_type = ":class:`str`"

    def type(self, value):
        try:
            cast_value = str(value)
        except ValueError:
            raise ParameterError("value cannot be cast to string: %r" % value)
        return cast_value


class LowerCaseString(String):
    """
    Lower case string
    """
    def type(self, value):
        cast_value = super(LowerCaseString, self).type(value)
        return cast_value.lower()


class UpperCaseString(String):
    """
    Upper case string
    """
    def type(self, value):
        cast_value = super(UpperCaseString, self).type(value)
        return cast_value.upper()


# ------------ others ---------------
class NonNullParameter(Parameter):
    """
    Non-nullable parameter
    """
    def cast(self, value):
        if value is None:
            raise ParameterError("value cannot be None")
        return self.type(value)


class PartsList(Parameter):
    def type(self, value):
        # Verify, raise exception for any problems
        if isinstance(value, (list, tuple)):
            from .part import Part  # avoid circular dependency
            for part in value:
                if not isinstance(part, Part):
                    raise ParameterError("value must be a list of Part instances")
        else:
            raise ParameterError("value must be a list")

        return value


# ------------ decorator(s) ---------------
def as_parameter(nullable=True, strict=True):
    """
    Decorate a container class as a functional :class:`Parameter` class
    for a :class:`ParametricObject`.

    :param nullable: if set, parameter's value may be Null
    :type nullable: :class:`bool`

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
    """
    def decorator(cls):
        base_class = Parameter if nullable else NonNullParameter

        return type(cls.__name__, (base_class,), {
            # Preserve text for documentation
            '__name__': cls.__name__,
            '__doc__': cls.__doc__,
            '__module__': cls.__module__,
            # Sphinx doc type string
            '_doc_type': ":class:`{class_name} <{module}.{class_name}>`".format(
                class_name=cls.__name__, module=__name__
            ),
            #
            'type': lambda self, value: cls(**value)
        })


    return decorator
