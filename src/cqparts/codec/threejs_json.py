
from . import Exporter, register_exporter
from ..part import Component, Part, Assembly

@register_exporter('json', Part)
class ThreeJSJsonExporter(Exporter):
    """
    **Name:** ``json``

    **Specification:** `three.js JSON model format v3 specification <https://github.com/mrdoob/three.js/wiki/JSON-Model-format-3>`_
    """

    def __call__(self, filename="out.json"):
        pass

    #if isinstance(component, Part):
