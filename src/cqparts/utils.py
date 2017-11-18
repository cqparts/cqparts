import cadquery

class property_buffered(object):
    """
    Buffer the result of a method on the class instance, similar to python builtin
    ``@property``, but the result is kept in memory until it's explicitly deleted.

    .. doctest::

        >>> from cqparts.utils import property_buffered
        >>> class A(object):
        ...     @property_buffered
        ...     def x(self):
        ...         print("x called")
        ...         return 100
        >>> a = A()
        >>> a.x
        x called
        100
        >>> a.x
        100
        >>> del a.x
        >>> a.x
        x called
        100

    Basis of class was sourced from the `funkybob/antfarm <https://github.com/funkybob/antfarm/blob/40a7cc450eba09a280b7bc8f7c68a807b0177c62/antfarm/utils/functional.py>`_ project.
    thanks to `@funkybob <https://github.com/funkybob>`_.
    """
    def __init__(self, getter, name=None):
        self.name = name or getter.__name__
        self.getter = getter
        self.__doc__ = getter.__doc__  # preserve sphinx autodoc docstring

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


def intersect(wp1, wp2, combine=True, clean=True):
    """
    Return geometric intersection between 2 cadquery.Workplane instances by
    exploiting.
    A n B = (A u B) - ((A - B) u (B - A))
    """
    solidRef = wp1.findSolid(searchStack=True, searchParents=True)

    if solidRef is None:
        raise ValueError("Cannot find solid to intersect with")
    solidToIntersect = None

    if isinstance(wp2, cadquery.CQ):
        solidToIntersect = wp2.val()
    elif isinstance(wp2, cadquery.Solid):
        solidToIntersect = wp2
    else:
        raise ValueError("Cannot intersect type '{}'".format(type(wp2)))

    newS = solidRef.intersect(solidToIntersect)

    if clean:
        newS = newS.clean()

    if combine:
        solidRef.wrapped = newS.wrapped

    return wp1.newObject([newS])

    #cp = lambda wp: wp.translate((0, 0, 0))
    #neg1 = cp(wp1).cut(wp2)
    #neg2 = cp(wp2).cut(wp1)
    #neg = neg1.union(neg2)
    #return cp(wp1).union(wp2).cut(neg)


def copy(wp):
    return wp.translate((0, 0, 0))


def fc_print(text):
    try:
        import FreeCAD
        FreeCAD.Console.PrintMessage(text)
    except Exception as e:
        print(text)
