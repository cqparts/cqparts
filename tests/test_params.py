from copy import copy

from base import CQPartsTest
from base import testlabel

# Unit under test
from cqparts.params import *
from cqparts.errors import ParameterError


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


class ParameterTypeTests(CQPartsTest):
    def test_float(self):
        p = Float(1.5)
        # default
        self.assertEqual(p.default, 1.5)
        self.assertIsInstance(p.default, float)
        # casting
        self.assertEqual(p.cast(1), 1)
        self.assertIsInstance(p.cast(1), float)
        self.assertRaises(ParameterError, p.cast, 'abc')
        # nullable
        self.assertIsNone(p.cast(None))

    def test_positive_float(self):
        p = PositiveFloat(1.5)

        self.assertEqual(p.default, 1.5)
        self.assertIsInstance(p.cast(1), float)
        self.assertIsInstance(p.cast(0), float)
        self.assertRaises(ParameterError, p.cast, 'abc')
        self.assertRaises(ParameterError, p.cast, -1)
        self.assertIsNone(p.cast(None))

    def test_float_range(self):
        p = FloatRange(-10, 10, 5)
        # default
        self.assertEqual(p.default, 5)
        self.assertIsInstance(p.default, float)
        # casting
        self.assertEqual(p.cast(0), 0)
        self.assertIsInstance(p.cast(0), float)
        self.assertEqual(p.cast(-10), -10)
        self.assertEqual(p.cast(10), 10)
        # outside range
        self.assertRaises(ParameterError, p.cast, -11)
        self.assertRaises(ParameterError, p.cast, 11)
        # nullable
        self.assertIsNone(p.cast(None))

    def test_int(self):
        p = Int(1)
        # default
        self.assertEqual(p.default, 1)
        self.assertIsInstance(p.default, int)
        # casting
        self.assertEqual(p.cast(15), 15)
        self.assertIsInstance(p.cast(10), int)
        self.assertRaises(ParameterError, p.cast, 'abc')
        # nullable
        self.assertIsNone(p.cast(None))

    def test_positive_int(self):
        p = PositiveInt(1)
        # default
        self.assertEqual(p.default, 1)
        self.assertIsInstance(p.default, int)
        # casting
        self.assertEqual(p.cast(15), 15)
        self.assertIsInstance(p.cast(10), int)
        self.assertRaises(ParameterError, p.cast, 'abc')
        # nullable
        self.assertIsNone(p.cast(None))

    def test_int_range(self):
        p = IntRange(-10, 10, 5)
        # default
        self.assertEqual(p.default, 5)
        self.assertIsInstance(p.default, int)
        # casting
        self.assertEqual(p.cast(0), 0)
        self.assertIsInstance(p.cast(0), int)
        self.assertEqual(p.cast(-10), -10)
        self.assertEqual(p.cast(10), 10)
        # outside range
        self.assertRaises(ParameterError, p.cast, -11)
        self.assertRaises(ParameterError, p.cast, 11)
        # nullable
        self.assertIsNone(p.cast(None))

    def test_bool(self):
        p = Boolean(True)
        # default
        self.assertEqual(p.default, True)
        self.assertIsInstance(p.default, bool)
        # casting
        self.assertEqualAndType(p.cast(0), False, bool)
        self.assertEqualAndType(p.cast(1), True, bool)
        self.assertEqualAndType(p.cast(''), False, bool)
        self.assertEqualAndType(p.cast('abc'), True, bool)
        # nullable
        self.assertIsNone(p.cast(None))

    def test_string(self):
        p = String('abc')
        # default
        self.assertEqual(p.default, 'abc')
        self.assertIsInstance(p.default, str)
        # casting
        self.assertEqual(p.cast('xyz'), 'xyz')
        self.assertEqual(p.cast(''), '')
        self.assertEqual(p.cast(1), '1')
        self.assertEqual(p.cast(1.2), '1.2')
        # nullable
        self.assertIsNone(p.cast(None))

    def test_lc_string(self):
        p = LowerCaseString('AbC')
        # default
        self.assertEqual(p.default, 'abc')
        self.assertIsInstance(p.default, str)
        # casting
        self.assertEqual(p.cast('XYZ'), 'xyz')
        self.assertEqual(p.cast(''), '')
        self.assertEqual(p.cast(1), '1')
        self.assertEqual(p.cast(1.2), '1.2')
        # nullable
        self.assertIsNone(p.cast(None))

    def test_uc_string(self):
        p = UpperCaseString('AbC')
        # default
        self.assertEqual(p.default, 'ABC')
        self.assertIsInstance(p.default, str)
        # casting
        self.assertEqual(p.cast('xyz'), 'XYZ')
        self.assertEqual(p.cast(''), '')
        self.assertEqual(p.cast(1), '1')
        self.assertEqual(p.cast(1.2), '1.2')
        # nullable
        self.assertIsNone(p.cast(None))

    def test_non_null(self):
        p1 = NonNullParameter(1)
        # not nullable
        self.assertRaises(ParameterError, p1.cast, None)

        # Inherited
        class P(Int, NonNullParameter):
            pass
        p2 = P(1)
        self.assertRaises(ParameterError, p2.cast, None)

    def test_partslist(self):
        p = PartsList()
