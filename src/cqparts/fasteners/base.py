import six

from ..part import Part, Assembly
from ..types import threads

from .params import HeadType, DriveType, ThreadType
from ..params import PositiveFloat


# ----------------- Fastener Components ---------------
# eg: for a nut & bolt, the nut is a component, the bolt is a component,
# and the combination of the two is a Fastener.
class FastenerMalePart(Part):
    """
    Male fastener part; with an external thread
    """
    head = HeadType(
        default=(
            'pan', {
                'diameter': 5.2,
                'height': 2.0,
                'fillet': 1.0,
            }
        ),
        doc="head type and parameters"
    )
    drive = DriveType(
        default=(
            'phillips', {
                'diameter': 3,
                'depth': 2.0,
                'width': 0.6,
            }
        ),
        doc="screw drive type and parameters"
    )
    thread = ThreadType(
        default=(
            threads.iso_262.ISO262Thread, {
                'radius': 3.0 / 2,
                #'pitch': 0.35,  # FIXME: causes invalid thread (see issue #1)
                'pitch': 0.7,
            }
        ),
        doc="thread type and parameters",
    )
    length = PositiveFloat(4.5)

    def make(self):
        # build Head
        obj = self.head.make()

        # build Thread (and union it to to the head)
        thread = self.thread.make(self.length + 0.01)
        thread = thread.translate((0, 0, -self.length))
        #return thread  # FIXME
        obj = obj.union(thread)

        # apply screw drive (if there is one)
        if self.drive:
            obj = self.drive.apply(
                obj,
                offset=self.head.get_face_offset()
            )

        return obj

    #def make_cutting_tool(


class FastenerFemale(Part):
    """
    Female fastener part; with an internal thread

    For a *nut* and *bolt*:

    * *nut* : female
    * *bolt* : male
    """

# ----------------- Fastener Base ---------------
class Fastener(Assembly):
    pass
