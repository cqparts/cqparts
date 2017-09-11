import six
import cadquery


class FastenerHead(object):
    diameter = 5.0
    height = 2

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            if not hasattr(self, key):
                raise ValueError("screw drive class {cls} does not accept a '{key}' parameter".format(
                    cls=repr(type(self)), key=key
                ))

            # Default value given to class
            default_value = getattr(self, key)

            # Cast value to the same type as the class default
            #   (mainly designed to turn ints to floats, or visa versa)
            if default_value is None:
                cast_value = value
            else:
                cast_value = type(default_value)(value)

            # Set given value
            setattr(self, key, cast_value)

    def make(self, offset=(0, 0, 0)):
        """
        Create fastener head solid and return it
        """
        raise NotImplementedError("make function not overridden in %r" % self)

    def get_face_offset(self):
        """
        Returns the screw drive origin offset relative to bolt's origin
        """
        return (0, 0, -self.height)


# Fastener Head register
#   Create your own fastener head like so...
#
#       @fastener_head('some_name')
#       class MyFastenerHead(FastenerHead):
#           my_param = 1.2
#
#           def make(self, offset=(0, 0, 0)):
#               head = cadquery.Workplane("XY") \
#                   .circle(self.diameter / 2) \
#                   .extrude(self.depth) \
#                   .faces(">Z") \
#                   .rect(self.my_param, self.my_param).extrude(0.3)
#               return head.translate(offset)

fastener_head_map = {}

def fastener_head(*names):
    assert all(isinstance(n, six.string_types) for n in names), "bad fastener head name"
    def inner(cls):
        """
        Add fastener head class to mapping
        """
        assert issubclass(cls, FastenerHead), "class must inherit from FastenerHead"
        for name in names:
            assert name not in fastener_head_map, "more than one fastener_head named '%s'" % name
            fastener_head_map[name] = cls
        return cls

    return inner
