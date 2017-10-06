from .errors import ParameterError

import logging
log = logging.getLogger(__name__)

class ParametricObject(object):
    """
    Parametric objects may be defined like so:

        >>> from cqparts.paramtypes import (
        ...     ParametricObject,
        ...     PositiveFloat, IntRange,
        ... )
        >>> class Foo(ParametricObject):
        ...     x = PositiveFloat(5)
        ...     i = IntRange(1, 10, 3)  # between 1 and 10, defaults to 3
        ...     blah = 100

        >>> a = Foo(x=3)  # a.x=3.0, a.i=3
        >>> a = Foo(i=8)  # a.x=5.0, a.i=8
        >>> a = Foo(i=11) # raises exception
        ParameterError: value of 11 outside the range {1, 10}
        >>> a = Foo(z=1)  # raises exception
        ParameterError: <class '__main__.Foo'> does not accept any of the parameters: ['z']
        >>> a = Foo(x='123')  # a.x=123.0, a.i=3
        >>> a = Foo(blah=200)  # raises exception, parameters be Parameter types
        ParameterError: <class '__main__.Foo'> does not accept any of the parameters: ['blah']
        >>> a = Foo(x=None)  # a.x is None, a.i=3  # any parameter can be set to None

    Internally to the object, parameters may be accessed simply with self.x, self.i
    These will always return the type defined

    """
    def __init__(self, **kwargs):
        # get all available parameters (recurse through inherited classes)
        def get_class_params(cls):
            params = set(
                k for (k, v) in cls.__dict__.items()
                if isinstance(v, Parameter)
            )
            for parent in cls.__bases__:
                params |= get_class_params(parent)
                # note: overridden class parameters will be duplicated here,
                #       but the params set() naturally ignores duplicates.
            return params

        params = get_class_params(type(self))

        # parameters explicitly defined during intantiation
        defined_params = set(kwargs.keys())

        # only accept a subset of params
        invalid_params = defined_params - params
        if invalid_params:
            raise ParameterError("{cls} does not accept any of the parameters: {keys}".format(
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
    def __init__(self, default):
        self.default = self.cast(default)

    def type(self, value):
        """Define's parameter's value class, to be overridden"""
        return value

    def cast(self, value):
        """
        Cast given value to the type dictated by this parameter type.
        (can be overridden to force non-nullable field)
        """
        if value is None:
            return None
        return self.type(value)


# ------------ float types ---------------
class Float(Parameter):
    def type(self, value):
        try:
            cast_value = float(value)
        except ValueError:
            raise ParameterError("value cannot be cast to a float: %r" % given_value)
        return cast_value


class PositiveFloat(Float):
    def type(self, value):
        cast_value = super(PositiveFloat, self).type(value)
        if cast_value < 0:
            raise ParameterError("value is not positive: %g" % cast_value)
        return cast_value


class FloatRange(Float):
    def __init__(self, min, max, default):
        self.min = min
        self.max = max
        super(FloatRange, self).__init__(default)

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
    def type(self, value):
        try:
            cast_value = int(value)
        except ValueError:
            raise ParameterError("value cannot be cast to an integer: %r" % value)
        return cast_value


class PositiveInt(Int):
    def type(self, value):
        cast_value = super(PositiveInt, self).type(value)
        if cast_value < 0:
            raise ParameterError("value is not positive: %g" % cast_value)
        return cast_value


class IntRange(Int):
    def __init__(self, min, max, default):
        self.min = min
        self.max = max
        super(IntRange, self).__init__(default)

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
    def type(self, value):
        try:
            cast_value = bool(value)
        except ValueError:
            raise ParameterError("value cannot be cast to bool: %r" % value)
        return cast_value


# ------------ string types ------------
class String(Parameter):
    def type(self, value):
        try:
            cast_value = str(value)
        except ValueError:
            raise ParameterError("value cannot be cast to string: %r" % value)
        return cast_value


class LowerCaseString(String):
    def type(self, value):
        cast_value = super(LowerCaseString, self).type(value)
        return cast_value.lower()


class UpperCaseString(String):
    def type(self, value):
        cast_value = super(UpperCaseString, self).type(value)
        return cast_value.upper()


# ------------ others ---------------
class NonNull(Parameter):
    def cast(self, value):
        if value is None:
            raise ParameterError("value cannot be None")
        return self.type(value)
