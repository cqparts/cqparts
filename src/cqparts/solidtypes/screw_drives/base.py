import six
import cadquery

from ...part import Part
from ...params import *

from ...utils import CoordSystem


class ScrewDrive(Part):
    diameter = PositiveFloat(3.0, doc="screw drive's diameter")
    depth = PositiveFloat(3.0, doc="depth of recess into driven body")

    def make(self):
        """
        Make the solid to use as a cutter, to make the screw-drive impression
        in another solid.

        :return: cutter solid
        :rtype: :class:`cadquery.Workplane`
        """
        raise NotImplementedError("%r implements no solid to subtract" % type(self))

    def apply(self, workplane, world_coords=CoordSystem()):
        """
        Application of screwdrive indentation into a workplane
        (centred on the given world coordinates).

        :param workplane: workplane with solid to alter
        :type workplane: :class:`cadquery.Workplane`
        :param world_coords: coorindate system relative to ``workplane`` to move
                             cutter before it's cut from the ``workplane``
        :type world_coords: :class:`CoordSystem`
        """

        self.world_coords = world_coords
        return workplane.cut(self.world_obj)


# ------ Registration
from ...search import (
    find as _find,
    search as _search,
    register as _register,
)
from ...search import common_criteria

module_criteria = {
    'module': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
