
from ..params import *

from .female import FemaleFastenerPart


class SquareNut(FemaleFastenerPart):
    edges = PositiveInt(4)


class HexNut(FemaleFastenerPart):
    edges = PositiveInt(6)


class HexFlangeNut(FemaleFastenerPart):
    edges = PositiveInt(6)
    washer = Boolean(True)
