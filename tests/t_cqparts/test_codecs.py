import unittest
import mock
import os
import tempfile
import shutil
from collections import defaultdict
from contextlib import contextmanager

from base import CQPartsTest, CodecRegisterTests
from base import testlabel
from base import suppress_stdout_stderr

# Unit(s) under test
from cqparts import codec
from cqparts import Part, Assembly, Component

from partslib import Box, Cylinder, CubeStack


class CodecTest(CQPartsTest):
    def assertFilesizeZero(self, filename):
        self.assertTrue(os.path.exists(filename))
        self.assertEqual(os.stat(filename).st_size, 0)

    def assertFilesizeNonZero(self, filename):
        self.assertTrue(os.path.exists(filename), "file does not exist: {!r}".format(filename))
        self.assertGreater(os.stat(filename).st_size, 0, "file is empty: {!r}".format(filename))

    @contextmanager
    def assertCreatesFile(self, filename, nonzero=True):
        """
        Assert that the code in context creates the given file

        :param filename: name of file to be created
        :type filename: :class:`str`
        """
        self.assertFalse(os.path.exists(filename), "file already exists: {}".format(filename))
        yield
        self.assertTrue(os.path.exists(filename), "file was not created: {}".format(filename))
        if nonzero:
            self.assertFilesizeNonZero(filename)


class CodecFileTest(CodecTest):
    def setUp(self):
        # Create a named temporary file to write to
        handle, self.filename = tempfile.mkstemp()
        os.close(handle)

    def tearDown(self):
        # Remove temporary file
        os.unlink(self.filename)


class CodecFolderTest(CodecTest):
    def setUp(self):
        # Create a temporary folder to populate, then delete
        self.foldername = tempfile.mkdtemp()

    def tearDown(self):
        # Remove temporary folder, and all content recursively
        shutil.rmtree(self.foldername)


# ------- Register Tests -------

class ExporterRegisterTests(CodecRegisterTests):
    def test_register(self):
        @codec.register_exporter('abc', Part)
        class Abc(codec.Exporter):
            pass
        self.assertEqual(codec.exporter_index, {'abc': {Part: Abc}})

    def test_get_registered(self):
        @codec.register_exporter('abc', Part)
        class Abc(codec.Exporter):
            pass
        self.assertIsInstance(codec.get_exporter(Box(), 'abc'), Abc)

    def test_get_registered_subtype(self):
        @codec.register_exporter('abc', Component)
        class Abc(codec.Exporter):
            pass
        self.assertIsInstance(codec.get_exporter(Box(), 'abc'), Abc)  # Part

    def test_bad_name(self):
        with self.assertRaises(TypeError):
            @codec.register_exporter(123, Part)  # bad name type
            class Abc(codec.Exporter):
                pass

    def test_bad_base_class(self):
        with self.assertRaises(TypeError):
            @codec.register_exporter('abc', int)  # base_class is not a Component
            class Abc(codec.Exporter):
                pass

    def test_re_register(self):
        @codec.register_exporter('abc', Part)
        class Abc(codec.Exporter):
            pass
        with self.assertRaises(TypeError):
            @codec.register_exporter('abc', Part)  # duplicate
            class Def(codec.Exporter):
                pass

    def test_base_class_conflict(self):
        @codec.register_exporter('abc', Component)
        class Abc(codec.Exporter):
            pass
        with self.assertRaises(TypeError):
            @codec.register_exporter('abc', Part)  # Part is a Component
            class Def(codec.Exporter):
                pass

    def test_no_exporter(self):
        with self.assertRaises(TypeError):
            codec.get_exporter(Box(), 'abc')

    def test_no_exporter_for_type(self):
        @codec.register_exporter('abc', Part)
        class Abc(codec.Exporter):
            pass
        with self.assertRaises(TypeError):
            codec.get_exporter(CubeStack(), 'abc')  # assembly


class ImporterRegisterTests(CodecRegisterTests):

    def test_register(self):
        @codec.register_importer('abc', Part)
        class Abc(codec.Importer):
            pass
        self.assertEqual(codec.importer_index, {'abc': {Part: Abc}})

    def test_get_registered(self):
        @codec.register_importer('abc', Part)
        class Abc(codec.Importer):
            pass
        self.assertIsInstance(codec.get_importer(Box, 'abc'), Abc)

    def test_get_registered_subtype(self):
        @codec.register_importer('abc', Component)
        class Abc(codec.Importer):
            pass
        self.assertIsInstance(codec.get_importer(Box, 'abc'), Abc)

    def test_bad_name(self):
        with self.assertRaises(TypeError):
            @codec.register_importer(123, Part)  # bad name type
            class Abc(codec.Importer):
                pass

    def test_bad_base_class(self):
        with self.assertRaises(TypeError):
            @codec.register_importer('abc', str)  # base_class is not a Component
            class Abc(codec.Importer):
                pass

    def test_re_register(self):
        @codec.register_importer('abc', Part)
        class Abc(codec.Importer):
            pass
        with self.assertRaises(TypeError):
            @codec.register_importer('abc', Part)  # duplicate register
            class Def(codec.Importer):
                pass

    def test_base_class_conflict(self):
        @codec.register_importer('abc', Component)
        class Abc(codec.Importer):
            pass
        with self.assertRaises(TypeError):
            @codec.register_importer('abc', Part)  # Part is a Component
            class Def(codec.Importer):
                pass

    def test_no_importer(self):
        with self.assertRaises(TypeError):
            codec.get_importer(Box, 'abc')

    def test_no_importer_for_type(self):
        @codec.register_importer('abc', Part)
        class Abc(codec.Importer):
            pass
        with self.assertRaises(TypeError):
            codec.get_importer(CubeStack, 'abc')


# ------- Specific Codecs -------
# --- Codec: step
@testlabel('codec', 'codc_step')
class TestStep(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.filename)
        cube.exporter('step')(self.filename)
        self.assertFilesizeNonZero(self.filename)

    def test_import(self):
        filename = 'test-files/cube.step'
        with suppress_stdout_stderr():
            cube = Part.importer('step')(filename)
            self.assertEqual(type(cube).__name__, 'cube_step')
            self.assertAlmostEqual(cube.bounding_box.xmin, -0.5, places=1)
            self.assertAlmostEqual(cube.bounding_box.xmax, 0.5, places=1)
            self.assertAlmostEqual(cube.local_obj.val().Volume(), 1)

    def test_import_unicode(self):
        filename = u'test-files/cube.step'
        with suppress_stdout_stderr():
            cube = Part.importer('step')(filename)
            self.assertAlmostEqual(cube.bounding_box.xmin, -0.5, places=1)
            self.assertAlmostEqual(cube.bounding_box.xmax, 0.5, places=1)
            self.assertAlmostEqual(cube.local_obj.val().Volume(), 1)

    @mock.patch('os.path.exists', mock.MagicMock(return_value=True))
    def test_mangle_numberstart(self):
        filename = 'test-files/0123_noexist.step'
        part = Part.importer('step')(filename)
        self.assertEqual(type(part).__name__, '_0123_noexist_step')

    def test_import_nofile(self):
        filename = 'test-files/noexist.step'
        with self.assertRaises(ValueError):
            # exception raised before
            Part.importer('step')(filename)

    @unittest.skip("OCC read of invalid step causes segfault")
    def test_import_badformat(self):
        filename = 'test-files/bad_format.step'  # file exists, but is not a valid STEP file
        thing = Part.importer('step')(filename)
        # exception not raised before object is formed
        with self.assertRaises(ValueError):
            with suppress_stdout_stderr():
                thing.local_obj

    def test_multipart_part(self):
        # When imported as a Part, geometry is unioned together
        filename = 'test-files/red_cube_blue_cylinder.step'
        with suppress_stdout_stderr():
            thing = Part.importer('step')(filename)
            # cylinder {5 < x < 15}, box {-10 < x < 0}
            # combined they should be {-10 < x < 15}
            self.assertAlmostEqual(thing.bounding_box.xmin, -10, places=0)  # {-11 < xmin < -9}
            self.assertAlmostEqual(thing.bounding_box.xmax, 15, places=0)  # {14 < xmax < 16}

    def test_multipart_assembly(self):
        # When imported as an Assembly, each individual mesh
        # is imported as a component Part of the resulting Assembly.
        filename = 'test-files/red_cube_blue_cylinder.step'
        with suppress_stdout_stderr():
            thing = Assembly.importer('step')(filename)
            self.assertEqual(len(thing.components), 2)
            self.assertEqual(len(thing.constraints), 2)


# --- Codec: json
@testlabel('codec', 'codec_json')
class TestJsonPart(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.filename)
        cube.exporter('json')(self.filename)
        self.assertFilesizeNonZero(self.filename)


@testlabel('codec', 'codec_json')
class TestJsonAssembly(CodecFolderTest):
    def test_export(self):
        obj = CubeStack()
        f = lambda n: os.path.join(self.foldername, n)
        obj.exporter('json')(f('out.json'))
        self.assertFalse(os.path.exists(f('out.json')))
        self.assertFilesizeNonZero(f('out.cube_a.json'))
        self.assertFilesizeNonZero(f('out.cube_b.json'))


# --- Codec: stl
@testlabel('codec', 'codec_stl')
class TestStl(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.filename)
        cube.exporter('stl')(self.filename)
        self.assertFilesizeNonZero(self.filename)


# TODO: temporarily removed
#       getting error on my virtual environment
#           LookupError: unknown encoding: unicode
#       cause unknown

# --- Codec: amf
@testlabel('codec', 'codec_amf')
class TestAmf(CodecFileTest):

    def test_export(self):
        cube = Box()
        self.assertEqual(os.stat(self.filename).st_size, 0)
        cube.exporter('amf')(self.filename)
        self.assertGreater(os.stat(self.filename).st_size, 0)


# --- Codec: svg
@testlabel('codec', 'codec_svg')
class TestSvg(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.filename)
        cube.exporter('svg')(self.filename)
        self.assertGreater(os.stat(self.filename).st_size, 0)


# --- Codec: gltf
@testlabel('codec', 'codec_gltf')
class TestGltf(CodecFolderTest):
    def test_part_not_embedded(self):
        cube = Box()
        cube.exporter('gltf')(
            os.path.join(self.foldername, 'cube.gltf'),
            embed=False,
        )
        self.assertFilesizeNonZero(os.path.join(self.foldername, 'cube.gltf'))
        self.assertFilesizeNonZero(os.path.join(self.foldername, 'cube.bin'))

    def test_part_embedded(self):
        cube = Box()
        cube.exporter('gltf')(
            os.path.join(self.foldername, 'cube.gltf'),
            embed=True,
        )
        self.assertFilesizeNonZero(os.path.join(self.foldername, 'cube.gltf'))
        self.assertFalse(os.path.exists(os.path.join(self.foldername, 'cube.bin')))

    def test_assembly(self):
        asm = CubeStack()
        asm.exporter('gltf')(
            os.path.join(self.foldername, 'asm.gltf')
        )
        self.assertFilesizeNonZero(os.path.join(self.foldername, 'asm.gltf'))
        for name in asm.components.keys():  # only works because it's a single layer assembly
            self.assertFilesizeNonZero(
                os.path.join(self.foldername, 'asm-%s.bin' % name)
            )

    def test_tolerance(self):
        def get_polycount(tolerance):
            obj = Cylinder(radius=10, length=10)  # new object per export
            exporter = obj.exporter('gltf')
            buffer = exporter.part_buffer(obj, tolerance=tolerance)
            return int(buffer.idx_size / 3)  # 3 vertex indices per polygon

        self.assertGreater(
            get_polycount(tolerance=0.01),
            get_polycount(tolerance=0.2)
        )

    # TODO: re-introduce test with OCC integration
    @unittest.skip("FreeCAD tessellate appears to cache")
    def test_tolerance_nocache(self):
        # note: same test as ``test_tolerance`` but without a creating a new object
        def get_polycount(obj, tolerance):
            exporter = obj.exporter('gltf')
            buffer = exporter.part_buffer(obj, tolerance=tolerance)
            return int(buffer.idx_size / 3)  # 3 vertex indices per polygon

        # tolerance: high -> low
        c1 = Cylinder(radius=10, length=10)
        self.assertLess(
            get_polycount(c1, tolerance=0.2),
            get_polycount(c1, tolerance=0.01)
        )

        # tolerance: low -> high
        c2 = Cylinder(radius=10, length=10)
        self.assertGreater(
            get_polycount(c2, tolerance=0.01),
            get_polycount(c2, tolerance=0.2)
        )


@testlabel('codec', 'codec_gltf')
class TestGltfBuffer(CQPartsTest):
    def test_indices_sizes(self):
        # 1 byte
        sb = codec.gltf.ShapeBuffer(max_index=0xff)
        self.assertEqual(sb.idx_bytelen, 1)
        sb.add_poly_index(1, 2, 3)
        self.assertEqual(sb.idx_size, 3)
        self.assertEqual(sb.idx_len, 3)

        # 2 bytes
        sb = codec.gltf.ShapeBuffer(max_index=0xff + 1)
        self.assertEqual(sb.idx_bytelen, 2)
        sb.add_poly_index(1, 2, 3)
        self.assertEqual(sb.idx_size, 3)
        self.assertEqual(sb.idx_len, 6)

        # 4 bytes
        sb = codec.gltf.ShapeBuffer(max_index=0xffff + 1)
        self.assertEqual(sb.idx_bytelen, 4)
        sb.add_poly_index(1, 2, 3)
        self.assertEqual(sb.idx_size, 3)
        self.assertEqual(sb.idx_len, 12)
