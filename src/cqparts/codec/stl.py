
import re

import cadquery

from . import Exporter, register_exporter
from .. import Part


@register_exporter('stl', Part)
class STLExporter(Exporter):
    """
    Export shape to STL format.

    =============== ======================
    **Name**        ``stl``
    **Exports**     :class:`Part`
    =============== ======================

    .. note::

        Object is passed to :meth:`cadquery.freecad_impl.exporters.exportShape`
        for exporting.

    """

    def __call__(self, filename='out.stl', world=False, tolerance=0.1):

        # Getting cadquery Shape
        workplane = self.obj.world_obj if world else self.obj.local_obj
        shape = workplane.val()

        # call cadquery exporter
        try:
            with open(filename, 'w') as fh:
                cadquery.freecad_impl.exporters.exportShape(
                    shape=shape,
                    exportType='STL',
                    fileLike=fh,
                    tolerance=tolerance,
                )
        except AttributeError:
            # If freecad_impl is not available (beacuse cadquery based on
            # PythonOCC is being uses), fall back onto an alternative export method
            from cadquery import exporters
            with open(filename, "w") as fh:
                exporters.exportShape(shape, exporters.ExportTypes.STL, fh, tolerance)
