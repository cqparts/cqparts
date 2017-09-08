
from .errors import ParameterTypeError


# ------------ float types ---------------
def t_float(given_value):
    try:
        value = float(given_value)
    except ValueError:
        raise ParameterTypeError("value cannot be cast to a float: %r" % given_value)
    return value


def t_pos_float(given_value):
    value = t_float(given_value)
    if value < 0:
        raise ParameterTypeError("value is not positive: %g" % value)
    return value


def t_float_range(min_value, max_value):
    def inner(given_value):
        value = t_float(given_value)
        if not (min_value <= value <= max_value):
            raise ParameterTypeError("value of %g out of bounds {%g,%g}" % (
                value, min_value, max_value
            ))
        return value
    return inner


# ------------ int types ---------------
def t_int(given_value):
    try:
        value = int(given_value)
    except ValueError:
        raise ParameterTypeError("value cannot be cast to an integer: %r" % given_value)
    return value


def t_pos_int(given_value):
    value = t_int(given_value)
    if value < 0:
        raise ParameterTypeError("value is not positive: %g" % value)
    return value


def t_int_range(min_value, max_value):
    def inner(given_value):
        value = t_int(given_value)
        if not (min_value <= value <= max_value):
            raise ParameterTypeError("value of %g out of bounds {%g,%g}" % (
                value, min_value, max_value
            ))
        return value
    return inner
