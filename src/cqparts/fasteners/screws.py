
from ..params import *

from .base import FastenerMalePart
from .params import HeadType, DriveType, ThreadType
from ..solidtypes import threads


class Screw(FastenerMalePart):
    head = HeadType(
        default=('countersunk', {
            'diameter': 9.5,
            'height': 3.5,
        }),
        doc="head type and parameters"
    )
    drive = DriveType(
        default=('phillips', {
            'diameter': 5.5,
            'depth': 2.5,
            'width': 1.15,
        }),
        doc="screw drive type and parameters"
    )
    thread = ThreadType(
        default=('triangular', {
            'diameter': 5,
            'pitch': 1.1,
            'angle': 20,
        }),
        doc="thread type and parameters",
    )
    neck_taper = FloatRange(0, 90, 15, doc="angle of neck's taper (0 is parallel with neck)")
    neck_length = PositiveFloat(7.5, doc="length of neck")
    length = PositiveFloat(25, doc="screw's length")
