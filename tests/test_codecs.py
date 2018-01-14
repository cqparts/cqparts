import unittest
import os
import tempfile
import shutil

from base import CQPartsTest
from base import testlabel
from base import suppress_stdout_stderr

# Unit(s) under test
from cqparts import codec
from cqparts import Part

from partslib import Box, CubeStack


class CodecTest(CQPartsTest):
    def assertFilesizeZero(self, filename):
        self.assertTrue(os.path.exists(filename))
        self.assertEqual(os.stat(filename).st_size, 0)

    def assertFilesizeNonZero(self, filename):
        self.assertTrue(os.path.exists(filename))
        self.assertGreater(os.stat(filename).st_size, 0)


class CodecFileTest(CodecTest):
    def setUp(self):
        # Create a named temporary file to write to
        self.temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp.close()  # to be opened and written by test

    def tearDown(self):
        # Remove temporary file
        os.unlink(self.temp.name)


class CodecFolderTest(CodecTest):
    def setUp(self):
        # Create a temporary folder to populate, then delete
        self.temp = tempfile.mkdtemp()

    def tearDown(self):
        # Remove temporary folder, and all content recursively
        shutil.rmtree(self.temp)


# ------- Tests -------

@testlabel('codec', 'codc_step')
class TestStep(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.temp.name)
        cube.exporter('step')(self.temp.name)
        self.assertFilesizeNonZero(self.temp.name)

    def test_import(self):
        filename = 'test-files/cube.step'
        with suppress_stdout_stderr():
            cube = Part.importer('step')(filename)
            self.assertAlmostEqual(cube.bounding_box.xmin, -0.5)
            self.assertAlmostEqual(cube.bounding_box.xmax, 0.5)

    def test_import_nofile(self):
        filename = 'test-files/noexist.step'
        with self.assertRaises(ValueError):
            # exception raised before
            Part.importer('step')(filename)

    def test_import_badformat(self):
        filename = 'test-files/bad_format.step'
        thing = Part.importer('step')(filename)
        # exception not raised before object is formed
        with self.assertRaises(ValueError):
            with suppress_stdout_stderr():
                thing.local_obj


@testlabel('codec', 'codec_json')
@unittest.skip("py3 updates and encoding issues")
class TestJson(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.temp.name)
        cube.exporter('json')(self.temp.name)
        self.assertFilesizeNonZero(self.temp.name)


@testlabel('codec', 'codec_stl')
class TestStl(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.temp.name)
        cube.exporter('stl')(self.temp.name)
        self.assertFilesizeNonZero(self.temp.name)


# TODO: temporarily removed
#       getting error on my virtual environment
#           LookupError: unknown encoding: unicode
#       cause unknown

@testlabel('codec', 'codec_amf')
@unittest.skip("py3 updates and encoding issues")
class TestAmf(CodecFileTest):

    def test_export(self):
        cube = Box()
        self.assertEqual(os.stat(self.temp.name).st_size, 0)
        cube.exporter('amf')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)


@testlabel('codec', 'codec_svg')
class TestSvg(CodecFileTest):
    def test_export(self):
        cube = Box()
        self.assertFilesizeZero(self.temp.name)
        cube.exporter('svg')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)


@testlabel('codec', 'codec_gltf')
class TestGltf(CodecFolderTest):
    def test_part_not_embedded(self):
        cube = Box()
        cube.exporter('gltf')(
            os.path.join(self.temp, 'cube.gltf'),
            embed=False,
        )
        self.assertFilesizeNonZero(os.path.join(self.temp, 'cube.gltf'))
        self.assertFilesizeNonZero(os.path.join(self.temp, 'cube.bin'))

    def test_part_embedded(self):
        cube = Box()
        cube.exporter('gltf')(
            os.path.join(self.temp, 'cube.gltf'),
            embed=True,
        )
        self.assertFilesizeNonZero(os.path.join(self.temp, 'cube.gltf'))
        self.assertFalse(os.path.exists(os.path.join(self.temp, 'cube.bin')))

    def test_assembly(self):
        asm = CubeStack()
        asm.exporter('gltf')(
            os.path.join(self.temp, 'asm.gltf')
        )
        self.assertFilesizeNonZero(os.path.join(self.temp, 'asm.gltf'))
        for name in asm.components.keys():  # only works because it's a single layer assembly
            self.assertFilesizeNonZero(
                os.path.join(self.temp, 'asm.%s.bin' % name)
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
