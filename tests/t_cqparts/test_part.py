from copy import copy
from math import sqrt

from base import CQPartsTest
from base import testlabel

import cadquery

# Unit under test
import cqparts
from cqparts.errors import MakeError
from cqparts.utils import CoordSystem
from cqparts.params import Int


class PreMaturePartTests(CQPartsTest):

    def test_no_make(self):
        class P(cqparts.Part):
            pass  # no content

        with self.assertRaises(NotImplementedError):
            P().local_obj

    def test_bad_make(self):
        class P(cqparts.Part):
            def make(self):
                return 1

        with self.assertRaises(MakeError):
            P().local_obj


class MakeSimpleTests(CQPartsTest):

    def test_auto_simplify(self):
        class P(cqparts.Part):
            def make(self):
                return cadquery.Workplane('XY').circle(1).extrude(1)

        # complex part
        p_complex = P()
        cbb = p_complex.local_obj.val().BoundingBox()  # complex geometry
        # simplified part
        p_simple = P(_simple=True)
        sbb = p_simple.local_obj.val().BoundingBox()  # simplified geometry

        self.assertAlmostEqual(cbb.xmin, sbb.xmin)
        self.assertAlmostEqual(cbb.xmax, sbb.xmax)
        self.assertAlmostEqual(cbb.ymin, sbb.ymin)
        self.assertAlmostEqual(cbb.ymax, sbb.ymax)
        self.assertAlmostEqual(cbb.zmin, sbb.zmin)
        self.assertAlmostEqual(cbb.zmax, sbb.zmax)

    def test_simplify(self):
        class P(cqparts.Part):
            def make(self):
                return cadquery.Workplane('XY').box(1,1,1)  # small box
            def make_simple(self):
                return cadquery.Workplane('XY').box(10,10,10)  # big box

        # complex geometry yields unit cube
        cbb = P().local_obj.val().BoundingBox()
        self.assertAlmostEqual((cbb.xmin, cbb.xmax), (-0.5, 0.5))

        # complex geometry yields cube with 10xunit sides
        sbb = P(_simple=True).local_obj.val().BoundingBox()
        self.assertAlmostEqual((sbb.xmin, sbb.xmax), (-5, 5))


class BuildCycleTests(CQPartsTest):

    def test_build(self):
        class P(cqparts.Part):
            def __init__(self, *args, **kwargs):
                self._flag = False
                super(P, self).__init__(*args, **kwargs)
            def make(self):
                self._flag = True
                return cadquery.Workplane('XY').box(1,1,1)
        p = P()
        self.assertFalse(p._flag)
        p.build()
        self.assertTrue(p._flag)

    def test_set_world_coords(self):
        class P(cqparts.Part):
            def make(self):
                return cadquery.Workplane('XY').box(1,1,1)
        p = P()
        self.assertIsNone(p.world_obj)
        p.world_coords = CoordSystem()
        self.assertIsNotNone(p.world_obj)
        p.world_coords = None
        self.assertIsNone(p.world_obj)

    def test_set_world_obj(self):
        class P(cqparts.Part):
            def make(self):
                return cadquery.Workplane('XY').box(1,1,1)
        p = P()
        p.world_coords = CoordSystem()
        self.assertIsNotNone(p.world_obj)
        with self.assertRaises(ValueError):
            p.world_obj = 'value is irrelevant'

    def test_set_local_obj(self):
        class P(cqparts.Part):
            def make(self):
                return cadquery.Workplane('XY').box(1, 1, 1)

        p = P()
        p.world_coords = CoordSystem(origin=(0,0,10))
        bb = p.world_obj.val().BoundingBox()
        self.assertAlmostEqual(bb.DiagonalLength, sqrt(3))
        self.assertAlmostEqual((bb.zmin, bb.zmax), (-0.5 + 10, 0.5 + 10))

        # change local
        p.local_obj = cadquery.Workplane('XY').box(10, 10, 10)
        bb = p.world_obj.val().BoundingBox()
        self.assertAlmostEqual(bb.DiagonalLength, sqrt(3) * 10)
        self.assertAlmostEqual((bb.zmin, bb.zmax), (-5 + 10, 5 + 10))


class CopyTests(CQPartsTest):

    def test_copy(self):
        class P(cqparts.Part):
            a = Int(10)
            def make(self):
                return cadquery.Workplane('XY').box(1, 1, 1)
        p1 = P()
        p2 = copy(p1)
