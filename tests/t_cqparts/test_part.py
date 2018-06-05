from copy import copy, deepcopy
from math import sqrt

from base import CQPartsTest
from base import testlabel

import cadquery

from partslib import Box

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

        self.assertBoundingBoxEqual(cbb, sbb)

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


class PartEqualityTests(CQPartsTest):

    def test_eq(self):
        obj_params = {'length': 1, 'width': 2, 'height': 3}
        b1 = Box(**obj_params)
        b2 = Box(**obj_params)

        # parts considered equal
        self.assertEqual(b1, b2)
        self.assertEqual(hash(b1), hash(b2))

        # geometry is independent
        self.assertIsNot(b1.local_obj, b2.local_obj)

    def test_eq_local_obj_change(self):
        obj_params = {'length': 1, 'width': 2, 'height': 3}
        b1 = Box(**obj_params)
        b2 = Box(**obj_params)
        self.assertEqual(b1, b2)

        # change local_obj of one
        b1.local_obj = b1.local_obj.faces('>Z').hole(1)

        # parts should no longer be equal
        self.assertNotEqual(b1, b2)


class PartCopyTests(CQPartsTest):

    def test_basic(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)

        # parts share the same geometry
        self.assertIs(b1.local_obj, b2.local_obj)

    def test_change_original(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)
        self.assertIs(b1.local_obj, b2.local_obj)

        # change local_obj of original
        b1.local_obj = b1.local_obj.faces('>Z').hole(1)
        self.assertIs(b1.local_obj, b2.local_obj)

    def test_change_copy(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)
        self.assertIs(b1.local_obj, b2.local_obj)

        # change local_obj of copy
        b2.local_obj = b2.local_obj.faces('>Z').hole(1)
        self.assertIs(b1.local_obj, b2.local_obj)

    def test_nested(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)
        b3 = copy(b2)

        self.assertIs(b1.local_obj, b3.local_obj)

    def test_world_obj_separate(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)

        b1.world_coords = CoordSystem((100, 0, 0))
        b2.world_coords = CoordSystem((-100, 0, 0))

        bb1 = b1.world_obj.val().BoundingBox()
        self.assertAlmostEqual(bb1.xmin, 95)
        self.assertAlmostEqual(bb1.xmax, 105)

        bb2 = b2.world_obj.val().BoundingBox()
        self.assertAlmostEqual(bb2.xmin, -105)
        self.assertAlmostEqual(bb2.xmax, -95)

    def test_world_obj_reset_orig(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)

        b1.world_coords = CoordSystem((100, 0, 0))
        b2.world_coords = CoordSystem((-100, 0, 0))

        self.assertEqual(len(b1.world_obj.faces().objects), 6)
        self.assertEqual(len(b2.world_obj.faces().objects), 6)

        # change original local_obj
        b1.local_obj = b1.local_obj.faces('>Z').hole(1)

        self.assertEqual(len(b1.world_obj.faces().objects), 7)
        self.assertEqual(len(b2.world_obj.faces().objects), 7)

    def test_world_obj_reset_copy(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)

        b1.world_coords = CoordSystem((100, 0, 0))
        b2.world_coords = CoordSystem((-100, 0, 0))

        self.assertEqual(len(b1.world_obj.faces().objects), 6)
        self.assertEqual(len(b2.world_obj.faces().objects), 6)

        # change original local_obj
        b2.local_obj = b2.local_obj.faces('>Z').hole(1)

        self.assertEqual(len(b1.world_obj.faces().objects), 7)
        self.assertEqual(len(b2.world_obj.faces().objects), 7)

    def test_params(self):
        b1 = Box(length=10, width=20, height=30)
        b2 = copy(b1)

        self.assertEqual(b1.length, b2.length)

        # change original
        b1.width = 200
        self.assertEqual(b1.width, b2.width)

        # change copy
        b2.height = 300
        self.assertEqual(b1.height, b2.height)


import unittest
@unittest.skip  # TODO: deepcopy not implemented yet
class DeepcopyTests(CQPartsTest):

    def test_basic(self):
        p1 = Box(length=5, width=10, height=3)
        p2 = deepcopy(p1)

        # a deepcopy does not build geometry
        self.assertIsNone(p1._local_obj)
        self.assertIsNone(p2._local_obj)

        # built parts independent
        self.assertIsInstance(p1.local_obj, cadquery.Workplane)
        self.asesrtIsInstance(p2.local_obj, cadquery.Workplane)
        self.assertIsNot(p1.local_obj, p2.local_obj)

    def test_buildorder_forward(self):
        p1 = Box(length=5, width=10, height=3)
        p2 = deepcopy(p1)

        # build and change original
        p1.build()
        self.assertEqual(len(p1.local_obj.faces().objects), 6)
        orig_obj = p1.local_obj
        p1.local_obj = p1.local_obj.faces('>Z').hole(1)
        self.assertEqual(len(p1.local_obj.faces().objects), 7)

        # copy not built yet
        self.assertIsNone(p2._local_obj)
        # build copy, should be copy of original object
        p2.build()
        self.assertEqual(len(p2.local_obj.faces().objects), 6)  # not 7
        self.assertIsNot(p2.local_obj, orig_obj)  # a copy, not a reference

    def test_buildorder_backward(self):
        p1 = Box(length=5, width=10, height=3)
        p2 = deepcopy(p1)

        # build and change original
        p2.build()
        self.assertEqual(len(p2.local_obj.faces().objects), 6)
        orig_obj = p2.local_obj
        p2.local_obj = p2.local_obj.faces('>Z').hole(1)
        self.assertEqual(len(p2.local_obj.faces().objects), 7)

        # copy not built yet
        self.assertIsNone(p1._local_obj)
        # build copy, should be copy of original object
        p1.build()
        self.assertEqual(len(p1.local_obj.faces().objects), 6)  # not 7
        self.assertIsNot(p1.local_obj, orig_obj)  # a copy, not a reference

    def test_post_modify(self):
        p1 = Box(length=5, width=10, height=3)  # 6 faces
        p1.local_obj = p1.local_obj.faces('>Z').hole(1)  # 7 faces

        p2 = deepcopy(p1)
        self.assertEqual(len(p2.local_obj.faces().objects), 7)

    def test_nested(self):
        p1 = Box(length=5, width=10, height=3)
        p2 = deepcopy(p1)
        p3 = deepcopy(p2)

        self.asesrtIsInstance(p3.local_obj, cadquery.Workplane)
