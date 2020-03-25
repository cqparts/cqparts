import os
import re

import cadquery

from . import Exporter, register_exporter
from . import Importer, register_importer
from .. import Part, Assembly
from ..constraint import Fixed


@register_exporter('step', Part)
class STEPExporter(Exporter):
    """
    Export shape to STEP format.

    =============== ======================
    **Name**        ``step``
    **Exports**     :class:`Part <cqparts.Part>`
    =============== ======================

    .. note::

        Object is passed to :meth:`cadquery.exporters.exportShape`
        for exporting.

    """

    def __call__(self, filename='out.step', world=False):
        # Getting cadquery Shape
        workplane = self.obj.world_obj if world else self.obj.local_obj
        shape = workplane.val()

        # call cadquery exporter
        with open(filename, 'w') as fh:
            cadquery.exporters.exportShape(
                shape=shape,
                exportType=cadquery.exporters.ExportTypes.STEP,
                fileLike=fh,
            )


class _STEPImporter(Importer):
    """
    Abstraction layer to avoid duplicate code for :meth:`_mangled_filename`.
    """
    @classmethod
    def _mangled_filename(cls, name):
        # ignore sub-directories
        name = os.path.basename(name)

        # encode to ascii (for a clean class name)
        name = name.encode('ascii', 'ignore')
        if type(name).__name__ == 'bytes':  # a python3 thing
            name = name.decode()  # type: bytes -> str

        # if begins with a number, inject a '_' at the beginning
        if re.search(r'^\d', name):
            name = '_' + name

        # replace non alpha-numeric characters with a '_'
        name = re.sub(r'[^a-z0-9_]', '_', name, flags=re.I)

        return name


@register_importer('step', Part)
class STEPPartImporter(_STEPImporter):
    """
    Import a shape from a STEP formatted file.

    =============== ======================
    **Name**        ``step``
    **Imports**     :class:`Part <cqparts.Part>`
    =============== ======================

    .. note::

        Step file is passed to :meth:`cadquery.importers.importShape` to do the
        hard work of extracting geometry.

    **Multi-part STEP**

    If the ``STEP`` file has multiple parts, all parts are unioned together to
    form a single :class:`Part <cqparts.Part>`.
    """

    def __call__(self, filename):
        if not os.path.exists(filename):
            raise ValueError("given file does not exist: '%s'" % filename)

        def make(self):
            return cadquery.importers.importShape(
                importType='STEP',
                fileName=filename,
            ).combine()

        # Create a class inheriting from our class
        imported_type = type(self._mangled_filename(filename), (self.cls,), {
            'make': make,
        })
        return imported_type()


@register_importer('step', Assembly)
class STEPAssemblyImporter(_STEPImporter):
    """
    Import a shape from a STEP formatted file.

    =============== ======================
    **Name**        ``step``
    **Imports**     :class:`Assembly <cqparts.Assembly>`
    =============== ======================

    .. note::

        Step file is passed to :meth:`cadquery.importers.importShape`
        to do the hard work of extracting geometry.

    **Multi-part STEP**

    This importer is intended for ``STEP`` files with multiple separated meshes
    defined.

    Each mesh is imported into a nested :class:`Part <cqparts.Part>` component.
    """

    def __call__(self, filename):
        if not os.path.exists(filename):
            raise ValueError("given file does not exist: '%s'" % filename)

        mangled_name = self._mangled_filename(filename)

        def make_components(self):
            # Part Builder
            def _get_make(nested_obj):
                def make(self):
                    return cadquery.Workplane("XY").newObject([nested_obj])
                return make

            # Import file
            obj = cadquery.importers.importShape(
                importType='STEP',
                fileName=filename,
            )

            components = {}
            for (i, o) in enumerate(obj.objects):
                idstr = '{:03g}'.format(i)
                part_clsname = "%s_part%s" % (mangled_name, idstr)
                part_cls = type(part_clsname, (Part, ), {
                    'make': _get_make(o),
                })
                components['{:03g}'.format(i)] = part_cls()

            return components

        def make_constraints(self):
            constraints = []
            for (key, part) in self.components.items():
                constraints.append(Fixed(part.mate_origin))
            return constraints

        # Create a class inheriting from our class
        imported_type = type(mangled_name, (self.cls,), {
            'make_components': make_components,
            'make_constraints': make_constraints,
        })
        return imported_type()
