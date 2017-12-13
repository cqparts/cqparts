import six
from copy import copy

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

        >>> a = Foo(i=8)  # a.x=5.0, a.i=8
        >>> a = Foo(i=11) # raises exception # doctest: +SKIP
        ParameterError: value of 11 outside the range {1, 10}
        >>> a = Foo(z=1)  # raises exception # doctest: +SKIP
        ParameterError: <class 'Foo'> does not accept any of the parameters: z
        >>> a = Foo(x='123', i='2')  # a.x=123.0, a.i=2
        >>> a = Foo(blah=200)  # raises exception, parameters must be Parameter types # doctest: +SKIP
        ParameterError: <class 'Foo'> does not accept any of the parameters: blah
        >>> a = Foo(x=None)  # a.x is None, a.i=3  # any parameter can be set to None

    Internally to the object, parameters may be accessed simply with self.x, self.i
    These will always return the type defined

    """
    def __init__(self, **kwargs):
        # get all available parameters (recurse through inherited classes)
        params = ParametricObject._get_class_params(type(self))

        # parameters explicitly defined during intantiation
        defined_params = set(kwargs.keys())

        # only accept a subset of params
        invalid_params = defined_params - params
        if invalid_params:
            raise ParameterError("{cls} does not accept parameter(s): {keys}".format(
                cls=repr(type(self)),
                keys=', '.join(sorted(invalid_params)),
            ))

        for key in params:
            param_def = getattr(type(self), key)

            # determine parameter value
            value = param_def.default
            if key in kwargs:
                value = param_def.cast(kwargs[key])

            # assign value to this instance
            setattr(self, key, value)

        self.initialize_parameters()

    @staticmethod
    def _get_class_params(cls):
        """
        Get all parameters for a given :class:`ParametricObject`.
        Including those inherited by base classes

        :param cls: child class of :class:`ParametricObject`
        :type cls: type
        :return: names of all settable parameters for the given class
        :rtype: set
        """
        params = set(
            k for (k, v) in cls.__dict__.items()
            if isinstance(v, Parameter)
        )
        for parent in cls.__bases__:
            params |= ParametricObject._get_class_params(parent)
            # note: overridden class parameters will be duplicated here,
            #       but the params set() naturally ignores duplicates.
        return params

    def _params_iter(self):
        param_names = ParametricObject._get_class_params(type(self))
        for name in sorted(param_names):
            yield (name, getattr(self, name))

    def __copy__(self):
        params_copy = dict((k, copy(v)) for (k, v) in self._params_iter())
        return type(self)(**params_copy)

    def __repr__(self):
        # <Branch: diameter=3.0, height=2.0, twist=0.0 @0x7f1ffbfcd790>
        params = list(self._params_iter())
        return "<{cls}: {params}>".format(
            cls=type(self).__name__,
            params=", ".join(
                "%s=%r" % (k, v)
                for (k, v) in params
                if not k.startswith('_')  # ignore private parameters
            ),
        )

    def initialize_parameters(self):
        """
        A palce to set default parameters more intelegently than just a
        simple default value.
        Executed just prior to exiting the __init__ function.
        Consider calling super.
        """
        pass


# ========================  Parameter Types  ========================
class Parameter(object):
    """
    Used to set parameters of a :class:`ParametricObject`.

    All instances of this class defined in a class' ``__dict__`` will be
    valid input to the object's constructor.
    """

    def __init__(self, default=None, doc=None):
        self.default = self.cast(default)
        self.doc = doc if isinstance(doc, six.string_types) else "[no description]"

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
        return self.doc

    _doc_type = '[unknown]'

    def _type(self):
        # for a sphinx line:
        #   :type my_param: <return is published here>
        return self._doc_type


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
