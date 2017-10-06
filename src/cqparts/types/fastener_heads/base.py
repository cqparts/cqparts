import six
import cadquery

# relative imports
from ...params import *

import logging
log = logging.getLogger(__name__)


class FastenerHead(ParametricObject):
    diameter = PositiveFloat(5.2)
    height = PositiveFloat(2.0)

    def make(self, offset=(0, 0, 0)):
        """
        Create fastener head solid and return it
        """
        raise NotImplementedError("make function not overridden in %r" % self)

    def get_face_offset(self):
        """
        Returns the screw drive origin offset relative to bolt's origin
        """
        return (0, 0, self.height)


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


def find(name):
    return fastener_head_map[name]
