

class buffered_property(object):
    """
    Buffer the result of a method on the class instance
    usage:
        >>> class A(x):
        ...     @buffered_property
        ...     def x(self):
        ...         print("x() called")
        ...         return 100
        >>> a = A()
        >>> a.x()
        x() called
        100
        >>> a.x()
        100
    """
    # source: https://github.com/funkybob/antfarm/blob/40a7cc450eba09a280b7bc8f7c68a807b0177c62/antfarm/utils/functional.py
    # thanks funkybob
    def __init__(self, getter, name=None):
        self.name = name or getter.__name__
        self.getter = getter

    def __get__(self, instance, owner):
        if instance is None:  # pragma: no cover
            return self
        instance.__dict__[self.name] = value = self.getter(instance)
        return value


def indicate_last(items):
    """
    iterate through list and indicate which item is the last, intended to
    assist tree displays of hierarchical content.
    :return: generator that yields (<bool>, <item>) where bool is True only on last entry
    """
    last_index = len(items) - 1
    for (i, item) in enumerate(items):
        is_last = (i == last_index)
        yield (is_last, item)
