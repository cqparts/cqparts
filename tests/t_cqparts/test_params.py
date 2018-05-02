from copy import copy

from base import CQPartsTest
from base import testlabel

from partslib import Box

# Unit under test
from cqparts.params import *
from cqparts.errors import ParameterError
from cqparts import Part, Assembly

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

    def test_bad_params(self):
        class P(ParametricObject):
            a = Float(1.2)
            b = Int(3)
        p1 = P(a=1, b=2)
        with self.assertRaises(ParameterError):
            p2 = P(a=1, b=2, c=3)  # no 'c' parameter


class DeserializeTestClass(ParametricObject):
    # class for:
    #   ParametricObjectSerializeTests.test_deserialize
    #   ParametricObjectSerializeTests.test_deserialize_baddata
    a = Float(1.2)
    b = Int(3)


class ParametricObjectSerializeTests(CQPartsTest):

    def test_serialize(self):
        class P(ParametricObject):
            a = Float(1.2)
            b = Int(3)

        data = P().serialize()

        # verify serialized structure
        self.assertEqual(set(data.keys()), set(['lib', 'class', 'params']))
        self.assertEqual(set(data['lib'].keys()), set(['name', 'version']))
        self.assertEqual(set(data['class'].keys()), set(['name', 'module']))
        self.assertEqual(data['params'], {'a': 1.2, 'b': 3})

    def test_deserialize(self):
        p1 = DeserializeTestClass()
        data = p1.serialize()
        p2 = ParametricObject.deserialize(data)

        # verify deserialized object is equal
        self.assertEqual(type(p1), type(p2))
        self.assertEqual((p1.a, p1.b), (p2.a, p2.b))

    def test_deserialize_bad_module(self):
        data = DeserializeTestClass().serialize()
        # assumption: test_deserialize passes
        data['class']['module'] += '__noexist__'
        with self.assertRaises(ImportError):
            ParametricObject.deserialize(data)

    def test_deserialize_bad_name(self):
        data = DeserializeTestClass().serialize()
        # assumption: test_deserialize passes
        data['class']['name'] += '__noexist__'
        with self.assertRaises(ImportError):
            ParametricObject.deserialize(data)


class ParameterTests(CQPartsTest):
    def test_sphinx_param(self):
        class MyParam(Parameter):
            pass

        # default
        p1 = MyParam()
        self.assertIsInstance(p1._param(), str)

        # custom
        p2 = MyParam(doc="custom doc")
        self.assertEqual(p2._param(), "custom doc")

    def test_sphinx_type(self):
        # default
        class MyParam1(Parameter):
            pass
        p1 = MyParam1()
        self.assertIsInstance(p1._type(), str)

        # custom
        class MyParam2(Parameter):
            _doc_type = "custom type"
        p2 = MyParam2()
        self.assertEqual(p2._type(), "custom type")

    def test_new(self):
        class MyParam(Parameter):
            pass
        p1 = MyParam(10)
        p2 = p1.new(20)
        self.assertIsInstance(p2, MyParam)
        self.assertEqual(p2.default, 20)


class ObjectWrapperTests(CQPartsTest):

    def test_as_parameter_nullable(self):

        class _ContainerParam(object):
            def __init__(self, a=1, b=2, c=3):
                self.a = a
                self.b = b
                self.c = c
        ContainerParam = as_parameter(nullable=True)(_ContainerParam)

        self.assertTrue(issubclass(ContainerParam, Parameter))

        class Thing(ParametricObject):
            foo = ContainerParam({'a': 10, 'b': 100}, doc="controls stuff")

        thing = Thing(foo={'a': 20})
        self.assertIsInstance(thing.foo, _ContainerParam)
        self.assertEqual(thing.foo.a, 20)
        self.assertEqual(thing.foo.b, 2)
        self.assertEqual(thing.foo.c, 3)

        thing = Thing(foo=None)
        self.assertIsNone(thing.foo)

    def test_as_parameter_not_nullable(self):

        @as_parameter(nullable=False)
        class ContainerParam(object):
            def __init__(self, a=1, b=2, c=3):
                self.a = a
                self.b = b
                self.c = c

        self.assertTrue(issubclass(ContainerParam, Parameter))

        class Thing(ParametricObject):
            foo = ContainerParam({'a': 10, 'b': 100}, doc="controls stuff")

        with self.assertRaises(ParameterError):
            Thing(foo=None)


class ParameterTypeTests(CQPartsTest):
    pass


class FloatTests(ParameterTypeTests):
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


class IntTests(ParameterTypeTests):
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


class BoolTests(ParameterTypeTests):
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


class StringTests(ParameterTypeTests):
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


class NonNullTests(ParameterTypeTests):
    def test_non_null(self):
        p1 = NonNullParameter(1)
        # not nullable
        self.assertRaises(ParameterError, p1.cast, None)

        # Inherited
        class P(Int, NonNullParameter):
            pass
        p2 = P(1)
        self.assertRaises(ParameterError, p2.cast, None)


class PartsListTests(ParameterTypeTests):
    def test_partslist(self):
        p = PartsList()
        (b1, b2) = (Box(), Box())
        v = p.cast([b1, b2])  # list
        self.assertIsInstance(v, (list, tuple))
        self.assertEqual([id(x) for x in v], [id(b1), id(b2)])

    def test_partstuple(self):
        p = PartsList()
        (b1, b2) = (Box(), Box())
        v = p.cast((b1, b2))  # tuple
        self.assertIsInstance(v, (list, tuple))
        self.assertEqual([id(x) for x in v], [id(b1), id(b2)])

    def test_bad_value(self):
        p = PartsList()
        with self.assertRaises(ParameterError):
            p.cast(1)

    def test_bad_part(self):
        p = PartsList()
        with self.assertRaises(ParameterError):
            p.cast([Box(), 1])


class ComponentRefTests(ParameterTypeTests):
    def test_part(self):
        p = ComponentRef()
        v = p.cast(Part())
        self.assertIsInstance(v, Part)

    def test_assembly(self):
        p = ComponentRef()
        v = p.cast(Assembly())
        self.assertIsInstance(v, Assembly)

    def test_nullable(self):
        p = ComponentRef()
        v = p.cast(None)
        self.assertIsNone(v)
