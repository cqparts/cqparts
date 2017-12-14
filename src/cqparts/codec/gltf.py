import os
import struct
import base64
from io import BytesIO
from itertools import chain
from copy import copy, deepcopy
import json

from . import Exporter, register_exporter
from .. import __version__
from ..part import Component, Part, Assembly


class WebGL:
    """
    Enumeration container (nothing special)

    .. doctest::

        >>> from cqparts.codec.gltf import WebGL
        >>> WebGL.ARRAY_BUFFER
        34962
    """

    # accessor.componentType
    BYTE = 5120
    UNSIGNED_BYTE = 5121
    SHORT = 5122
    UNSIGNED_SHORT = 5123
    UNSIGNED_INT = 5125
    FLOAT = 5126

    # bufferView.target
    ARRAY_BUFFER = 34962
    ELEMENT_ARRAY_BUFFER = 34963

    # mesh.primative.mode
    POINTS = 0
    LINES = 1
    LINE_LOOP = 2
    LINE_STRIP = 3
    TRIANGLES = 4
    TRIANGLE_STRIP = 5
    TRIANGLE_FAN = 6



class ShapeBuffer(object):
    """
    Write byte buffer for a set of polygons

    To create a buffer for a single polygon:

    .. doctest::

        >>> from cqparts.codec.gltf import ShapeBuffer
        >>> sb = ShapeBuffer()

        >>> # Populate data
        >>> sb.add_vertex(0, 0, 0)  # [0]
        >>> sb.add_vertex(1, 0, 0)  # [1]
        >>> sb.add_vertex(0, 1, 0)  # [2]
        >>> sb.add_poly_index(0, 1, 2)

        >>> # write to file
        >>> with open('single-poly.bin', 'wb') as fh:  # doctest: +SKIP
        ...     for chunk in sb.buffer_iter():  # doctest: +SKIP
        ...         fh.write(chunk)  # doctest: +SKIP

        >>> # get sizes (relevant for offsets)
        >>> (sb.vert_len, sb.vert_size)
        (36L, 3L)
        >>> (sb.idx_len, sb.idx_size)
        (6L, 3L)
    """
    def __init__(self):
        self.vert_data = BytesIO()  # POSITION
        self.idx_data = BytesIO()  # indices

        self.vert_min = None
        self.vert_max = None

    @property
    def vert_len(self):
        """
        Number of bytes in ``vert_data`` buffer.
        """
        return self.vert_data.tell()

    @property
    def vert_offset(self):
        """
        Offset (in bytes) of the ``vert_data`` buffer.
        """
        return 0

    @property
    def vert_size(self):
        r"""
        Size of ``vert_data`` in groups of 3 floats
        (ie: number of :math:`3 \times 4` byte groups)

        See `Accessor Element Size <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#accessor-element-size>`_
        in the glTF docs for clarification.
        """
        # size of position buffer, in groups of 3 floats
        return self.vert_len / (3 * 4)

    @property
    def idx_len(self):
        """
        Number of bytes in ``idx_data`` buffer.
        """
        return self.idx_data.tell()

    @property
    def idx_offset(self):
        """
        Offset (in bytes) of the ``idx_data`` buffer.
        """
        return self.vert_len

    @property
    def idx_size(self):
        """
        Size of ``idx_data`` in UINTs.
        (ie: number of 2 byte groups)

        See `Accessor Element Size <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#accessor-element-size>`_
        in the glTF docs for clarification.
        """
        return self.idx_len / 2

    def __len__(self):
        return self.vert_len + self.idx_len

    def add_vertex(self, x, y, z):
        """
        Add a ``VEC3`` of ``floats`` to the ``vert_data`` buffer
        """
        self.vert_data.write(
            struct.pack('<f', x) +
            struct.pack('<f', y) +
            struct.pack('<f', z)
        )

        # retain min/max values
        # FIXME: efficiency
        # min
        if self.vert_min is None:
            self.vert_min = [x, y, z]
        else:
            self.vert_min[0] = min(self.vert_min[0], x)
            self.vert_min[1] = min(self.vert_min[1], y)
            self.vert_min[2] = min(self.vert_min[2], z)
        # max
        if self.vert_max is None:
            self.vert_max = [x, y, z]
        else:
            self.vert_max[0] = max(self.vert_max[0], x)
            self.vert_max[1] = max(self.vert_max[1], y)
            self.vert_max[2] = max(self.vert_max[2], z)

    def add_poly_index(self, i, j, k):
        """
        Add 3 ``SCALAR`` of ``uint`` (2 bytes each) to the ``idx_data`` buffer.
        """
        self.idx_data.write(
            struct.pack('<H', i) +
            struct.pack('<H', j) +
            struct.pack('<H', k)
        )

    def buffer_iter(self, block_size=1024):
        """
        Iterate through chunks of the vertices, and indices buffers seamlessly.

        .. note::

            To see a usage example, look at the :class:`ShapeBuffer` description.
        """
        streams = (
            self.vert_data,
            self.idx_data,
        )

        # Chain streams seamlessly
        for stream in streams:
            stream.seek(0)
            for chunk in stream.read(block_size):
                yield chunk

        # When complete, each stream position should be reset;
        #   back to the end of the stream.

    def read(self):
        """
        Read buffer out as a single stream.

        .. warning::

            Avoid using this function!

            **Why?** This is a *convenience* function; it doesn't encourage good
            memory management.

            **Instead:** Wherever possible, please use :meth:`buffer_iter`.
        """
        buffer = BytesIO()
        for chunk in self.buffer_iter():
            buffer.write(chunk)
        buffer.seek(0)
        return buffer.read()


@register_exporter('gltf', Component)
class GLTFExporter(Exporter):
    u"""
    Export :class:`Part <cqparts.part.Part>` or
    :class:`Assembly <cqparts.part.Assembly>` to a *glTF 2.0* format.

    =============== ======================
    **Name**        ``gltf``
    **Exports**     :class:`Part <cqparts.part.Part>` & :class:`Assembly <cqparts.part.Assembly>`
    **Spec**        `glTF 2.0 <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0>`_
    =============== ======================

    **Embedding vs .bin Files:** default generates ``.bin`` files

    If ``embed`` is ``True`` when :meth:`calling <__call__>`, then all data is
    stored in the output ``.gltf`` file.
    However this is very inefficient, for larger, more complex models when
    loading on a web-interface.

    When not embedded, all geometry will be stored as binary ``.bin``
    files in the same directory as the root ``.gltf`` file.

    For example, if we use the ``car`` from :ref:`tutorial_assembly`,
    with the hierarchy::

        car
        \u251c\u25cb chassis
        \u251c\u2500 front_axle
        \u2502   \u251c\u25cb axle
        \u2502   \u251c\u25cb left_wheel
        \u2502   \u2514\u25cb right_wheel
        \u2514\u2500 rear_axle
            \u251c\u25cb axle
            \u251c\u25cb left_wheel
            \u2514\u25cb right_wheel

    When exported, a ``.bin`` file will be created for each
    :class:`Part <cqparts.part.Part>` (denoted by a ``\u25cb``).

    So the following files will be generated::

        car.gltf
        car.chassis.bin
        car.front_axle.axle.bin
        car.front_axle.left_wheel.bin
        car.front_axle.right_wheel.bin
        car.rear_axle.axle.bin
        car.rear_axle.left_wheel.bin
        car.rear_axle.right_wheel.bin

    The ``car.gltf`` will reference each of the ``.bin`` files.

    The ``car.gltf`` and **all** ``.bin`` files should be web-hosted to serve
    the scene correctly.

    .. todo::

        In this example, all *wheels* and *axles* are the same, they should
        only generate a single buffer.

        But how to definitively determine :class:`Part <cqparts.part.Part>`
        instance equality?


    """

    TEMPLATE = {
        # Static values
        "asset": {
            "generator": "cqparts_%s" % __version__,
            "version": "2.0"  # glTF version
        },
        "scene": 0,

        # Populated by adding parts
        "scenes": [{"nodes": [0]}],
        "nodes": [
            {
                "children": [1],  # may be replaced before exporting
                "matrix": [  # scene rotation
                    1.0, 0.0, 0.0, 0.0,
                    0.0, 0.0,-1.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 1.0,
                ],
            },
        ],
        "meshes": [],
        "accessors": [],
        "materials": [],
        "bufferViews": [],
        "buffers": [],
    }

    # error tolerance of vertices to true face value, only relevant for curved surfaces.
    tolerance = 0.01

    def __init__(self, *args, **kwargs):
        super(GLTFExporter, self).__init__(*args, **kwargs)

        # Initialize
        self.gltf_dict = deepcopy(self.TEMPLATE)

    def __call__(self, filename='out.gltf', embed=False):
        """
        :param filename: name of ``.gltf`` file to export
        :type filename: :class:`str`
        :param embed: if True, binary content is embedded in json object.
        :type embed: :class:`bool`
        """

        def add(obj, filename, name):
            split = os.path.splitext(filename)

            if isinstance(obj, Assembly):
                obj.solve()
                for (child_name, child) in obj.components.items():
                    add(
                        child,
                        filename=None if embed else ("%s.%s%s" % (split[0], child_name, split[1])),
                        name="%s.%s" % (name, child_name)
                    )
            else:
                self.add_part(
                    obj,
                    filename=None if embed else filename,
                    name=name,
                )

        split = os.path.splitext(filename)
        add(
            obj=self.obj,
            filename=None if embed else ("%s.bin" % split[0]),
            name=os.path.splitext(os.path.basename(filename))[0]
        )

        # make sure node[0] has all other objects as children
        self.gltf_dict['nodes'][0]['children'] = list(range(1, len(self.gltf_dict['nodes'])))

        with open(filename, 'w') as fh:
            fh.write(json.dumps(self.gltf_dict, indent=2, sort_keys=True))

    @classmethod
    def part_mesh(cls, part):
        """
        Convert a part's object to a mesh.

        :param part: part being converted to a mesh
        :type part: :class:`Part <cqparts.part.Part>`
        :param world: if True, world coordinates are used
        :type world: :class:`bool`
        :return: list of (<vertices>, <indexes>)
        :rtype: :class:`tuple`

        Returned mesh format::

            <return value> = (
                [FreeCAD.Base.Vector(x, y, z), ... ],  # list of vertices
                [(i, j, k), ... ],  # indexes of vertices making a polygon
            )
        """
        workplane = part.local_obj  # cadquery.CQ instance
        shape = workplane.val()  # expecting a cadquery.Solid instance
        tess = shape.tessellate(cls.tolerance)
        return tess

    @classmethod
    def part_buffer(cls, part):
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
            >>> buff = cube.exporter('gltf').part_buffer(cube)

            >>> import base64
            >>> {'uri': "data:{mimetype};base64,{data}".format(
            ...     mimetype="application/octet-stream",
            ...     data=base64.b64encode(buff.read()).decode('ascii'),
            ... )}
            {'uri': 'data:application/octet-stream;base64,AAAAvwAAAD8AAIA/AAAAvwAAAD8AAAAAAAAAvwAAAL8AAIA/AAAAvwAAAL8AAAAAAAAAPwAAAL8AAIA/AAAAPwAAAD8AAAAAAAAAPwAAAD8AAIA/AAAAPwAAAL8AAAAAAAABAAIAAQADAAIABAAFAAYABAAHAAUAAwAHAAIAAgAHAAQAAAAFAAEABgAFAAAAAwABAAcABwABAAUABAAAAAIABgAAAAQA'}

        """
        # binary save done here:
        #    https://github.com/KhronosGroup/glTF-Blender-Exporter/blob/master/scripts/addons/io_scene_gltf2/gltf2_export.py#L112

        buff = ShapeBuffer()

        # Push mesh to ShapeBuffer
        (vertices, indices) = cls.part_mesh(part)
        for vert in vertices:
            buff.add_vertex(vert.x, vert.y, vert.z)
        for (i, j, k) in indices:
            buff.add_poly_index(i, j, k)

        return buff

    def add_part(self, part, filename=None, name=''):
        # ----- Adding to: buffers
        buff = self.part_buffer(part)

        buffer_index = len(self.gltf_dict['buffers'])
        buffer_dict = {
            "byteLength": len(buff),
        }
        if filename:
            # write file
            with open(filename, 'wb') as fh:
                for chunk in buff.buffer_iter():
                    fh.write(chunk)
            buffer_dict['uri'] = os.path.basename(filename)
        else:
            # embed buffer data in URI
            buffer_dict['uri'] = "data:{mimetype};base64,{data}".format(
                mimetype="application/octet-stream",
                data=base64.b64encode(buff.read()).decode('ascii'),
            )

        self.gltf_dict['buffers'].append(buffer_dict)

        # ----- Adding: bufferViews
        bufferView_index = len(self.gltf_dict['bufferViews'])

        # vertices view
        view = {
            "buffer": buffer_index,
            "byteOffset": buff.vert_offset,
            "byteLength": buff.vert_len,
            "byteStride": 12,
            "target": WebGL.ARRAY_BUFFER,
        }
        self.gltf_dict['bufferViews'].append(view)
        bufferView_index_vertices = bufferView_index

        # indices view
        view = {
            "buffer": buffer_index,
            "byteOffset": buff.idx_offset,
            "byteLength": buff.idx_len,
            "target": WebGL.ELEMENT_ARRAY_BUFFER,
        }
        self.gltf_dict['bufferViews'].append(view)
        bufferView_index_indices = bufferView_index + 1

        # ----- Adding: accessors
        accessor_index = len(self.gltf_dict['accessors'])

        # vertices accessor
        accessor = {
            "bufferView": bufferView_index_vertices,
            "byteOffset": 0,
            "componentType": WebGL.FLOAT,
            "count": buff.vert_size,
            "min": buff.vert_min,
            "max": buff.vert_max,
            "type": "VEC3",
        }
        self.gltf_dict['accessors'].append(accessor)
        accessor_index_vertices = accessor_index

        # indices accessor
        accessor = {
            "bufferView": bufferView_index_indices,
            "byteOffset": 0,
            "componentType": WebGL.UNSIGNED_SHORT,
            "count": buff.idx_size,
            "type": "SCALAR",
        }
        self.gltf_dict['accessors'].append(accessor)
        accessor_index_indices = accessor_index + 1

        # ----- Adding: meshes
        mesh_index = len(self.gltf_dict['meshes'])
        mesh = {
            "primitives": [
                {
                    "attributes": {
                        "POSITION": accessor_index_vertices,
                    },
                    "indices": accessor_index_indices,
                    "mode": WebGL.TRIANGLES,
                    #"material": 0,  # TODO: add materials
                }
            ],
            "name": name,
        }
        self.gltf_dict['meshes'].append(mesh)

        # ----- Adding: nodes
        node_index = len(self.gltf_dict['nodes'])
        node = {
            "mesh": mesh_index,
        }
        self.gltf_dict['nodes'].append(node)


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
            "max": [ 1.0,  1.0,  1.0],
            "min": [-1.0, -1.0, -1.0],
            "type": "VEC3",
        },
        {
            "bufferView": 1,
            "byteOffset": 288,
            "componentType": 5126,
            "count": 24,
            "max": [ 0.5,  0.5,  0.5],
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
