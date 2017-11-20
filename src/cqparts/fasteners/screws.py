
from ..part import Part
from ..params import (
    Float, PositiveFloat,
    LowerCaseString,
)

class Screw(Part):
    screw_drive = LowerCaseString('phillips')
    thread = LowerCaseString('triangular')
