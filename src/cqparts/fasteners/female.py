

from ..part import Part
from ..params import *
from .params import *

from ..solidtypes.fastener_heads.driven import DrivenFastenerHead


class FemaleFastenerPart(DrivenFastenerHead):
    """
    Female fastener part; with an internal thread

    For a *nut* and *bolt*:

    * *nut* : female
    * *bolt* : male
    """

    width = PositiveFloat(8, doc="width of tool reqiured to fasten nut")
    height = PositiveFloat(3, doc="height of nut")
    chamfer_top = Boolean(True, doc="if chamfer is set, top edges are chamfered")
    chamfer_base = Boolean(True, doc="if chamfer is set, base edges are chamfered")

    thread = ThreadType(
        default=('iso262', {  # M5
            'diameter': 5,
            'pitch': 0.5,
        }),
        doc="thread type and parameters",
    )

    def initialize_parameters(self):
        super(FemaleFastenerPart, self).initialize_parameters()
        # force thread to be inner
        self.thread.inner = True
        # force thread height to that of the nut
        self.thread.length = self.height

    def make(self):
        # mirror inherited object
        nut = super(FemaleFastenerPart, self).make().mirror(mirrorPlane="XY")
        # +z direction is maintained for male & female parts, but the object
        # resides on the opposite side of the XY plane

        # Cut thread
        thread = self.thread.local_obj.translate((0, 0, -self.height))
        nut = nut.cut(thread)
        return nut
