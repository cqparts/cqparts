import os
import tempfile

from base import CQPartsTest

# Unit(s) under test
from cqparts import codec
from cqparts import Part

from cqparts.basic.primatives import Cube

class CodecTest(CQPartsTest):
    def setUp(self):
        # Create a named temporary file to write to
        self.temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp.close()  # to be opened and written by test

    def tearDown(self):
        # Remove temporary file
        os.unlink(self.temp.name)


class TestStep(CodecTest):

    def test_export(self):
        cube = Cube()
        self.assertEqual(os.stat(self.temp.name).st_size, 0)
        cube.exporter('step')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)

    def test_import(self):
        filename = 'test-files/cube.step'
        cube = Part.importer('step')(filename)
        self.assertAlmostEqual(cube.bounding_box.xmin, -0.5)
        self.assertAlmostEqual(cube.bounding_box.xmax, 0.5)


class TestJson(CodecTest):

    def test_export(self):
        cube = Cube()
        self.assertEqual(os.stat(self.temp.name).st_size, 0)
        cube.exporter('json')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)


class TestStl(CodecTest):

    def test_export(self):
        cube = Cube()
        self.assertEqual(os.stat(self.temp.name).st_size, 0)
        cube.exporter('stl')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)

class TestAmf(CodecTest):

    def test_export(self):
        cube = Cube()
        self.assertEqual(os.stat(self.temp.name).st_size, 0)
        cube.exporter('amf')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)


class TestSvg(CodecTest):

    def test_export(self):
        cube = Cube()
        self.assertEqual(os.stat(self.temp.name).st_size, 0)
        cube.exporter('svg')(self.temp.name)
        self.assertGreater(os.stat(self.temp.name).st_size, 0)
