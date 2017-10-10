from copy import copy

from base import CQPartsTest

# Units under test
from cqparts.params import ParametricObject
from cqparts.params import (
    Float, PositiveFloat, FloatRange,
    Int, PositiveInt, IntRange,
    Boolean,
    LowerCaseString, UpperCaseString,
)

class ParametricObjectTests(CQPartsTest):
    def test_inherited_params(self):
        class T1(ParametricObject):
            a = Float(1.2)
            b = Int(3)
        class T2(T1):
            c = IntRange(0, 10, 5)
        self.assertHasAttr(T2(), 'a')
        self.assertHasAttr(T2(), 'c')
        self.assertEqual(T2().a, 1.2)
        self.assertEqual(T2(a=5.2).a, 5.2)

    def test_copy(self):
        class T(ParametricObject):
            a = Float(1.2)
            b = Int(5)

        t1 = T(a=2.1)
        t2 = copy(t1)
        # copy is a copy
        self.assertEqual(t1.a, t2.a)
        self.assertEqual(t1.b, t2.b)
        # changing t1 values doesn't change t2 values
        t1.a = 4.9
        t1.b = 8
        self.assertNotEqual(t1.a, t2.a)
        self.assertNotEqual(t1.b, t2.b)
