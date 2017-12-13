import base64

from . import Exporter, register_exporter
from .. import __version__
from ..part import Component, Part, Assembly


@register_exporter('gltf', Component)
class GLTFExporter(Exporter):
    """
    Export :class:`Part <cqparts.part.Part>` or
    :class:`Assembly <cqparts.part.Assembly>` to a *glTF 2.0* format.

    =============== ======================
    **Name**        ``gltf``
    **Exports**     :class:`Part <cqparts.part.Part>` & :class:`Assembly <cqparts.part.Assembly>`
    **Spec**        `glTF 2.0 <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0>`_
    =============== ======================

    """

    @classmethod
    def part_buffer(cls, part, world=False):
        """
        Export part's geometry as a
        `glTF 2.0 <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0>`_
        asset binary stream.

        :param world: if True, use world coordinates, otherwise use local
        :type world: :class:`bool`
        :return: byte sream of exported geometry
        :rtype: :class:`BytesIO`

        To embed binary model data into a 'uri', you can:

        .. doctest::

            >>> import cqparts
            >>> from cqparts.basic.primatives import Cube

            >>> cube = Cube()
            >>> data = cqparts.codec.GLTFExporter.part_buffer(some_part)

            >>> import base64
            >>> {'uri': "data:{mimetype};base64,{data}".format(
            ...     mimetype="application/octet-stream",
            ...     data=base64.b64encode(data).decode('ascii'),
            ... )}

        """
        data = BytesIO()

        # binary save done here:
        #    https://github.com/KhronosGroup/glTF-Blender-Exporter/blob/master/scripts/addons/io_scene_gltf2/gltf2_export.py#L112

        # TODO: this is a work in progress


TEMPLATE = {
    "asset": {
        "generator": "cqparts_%s" % __version__,
        "version": "2.0"  # glTF version
    },
    "scene": 0,
    "scenes": [{"nodes": [0]}],
    "nodes": [
        # https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#nodes-and-hierarchy
        {
            "children": [
                1
            ],
            # TOOD: add scale + translation
            "matrix": [
                1.0, 0.0, 0.0, 0.0,
                0.0, 0.0,-1.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ],
        },
        {
            "mesh": 0,
        },
    ],
    "meshes": [
        {
            "primitives": [
                {
                    "attributes": {
                        "NORMAL": 1,
                        "POSITION": 2,
                    },
                    "indices": 0,
                    "mode": 4,
                    "material": 0,
                }
            ],
            "name": "Mesh",
        }
    ],
    "accessors": [
        {
            "bufferView": 0,
            "byteOffset": 0,
            "componentType": 5123,
            "count": 36,
            "max": [23],
            "min": [0],
            "type": "SCALAR",
        },
        {
            "bufferView": 1,
            "byteOffset": 0,
            "componentType": 5126,
            "count": 24,
            "max": [1.0, 1.0, 1.0],
            "min": [-1.0, -1.0, -1.0],
            "type": "VEC3",
        },
        {
            "bufferView": 1,
            "byteOffset": 288,
            "componentType": 5126,
            "count": 24,
            "max": [0.5, 0.5, 0.5],
            "min": [-0.5, -0.5, -0.5],
            "type": "VEC3",
        },
    ],
    "materials": [
        {
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.8, 0.0, 0.0, 1.0],  # rbta
                "metallicFactor": 0.0,
            },
            "name": "Red",
        },
    ],
    "bufferViews": [
        {
            "buffer": 0,
            "byteOffset": 576,
            "byteLength": 72,
            "target": 34963,
        },
        {
            "buffer": 0,
            "byteOffset": 0,
            "byteLength": 576,
            "byteStride": 12,
            "target": 34962,
        },
    ],
    "buffers": [
        {
            "byteLength": 648,
            "uri": "Box0.bin",
        },
    ],
}
