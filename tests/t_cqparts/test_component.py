
from base import CQPartsTest, CodecRegisterTests
from base import testlabel

# Unit(s) under test
import cqparts
from cqparts.utils import CoordSystem
from cqparts.constraint import Mate
from cqparts.constraint.mate import mate
from cqparts import codec


class ComponentTests(CQPartsTest):

    def test_premature(self):
        c = cqparts.Component()
        with self.assertRaises(NotImplementedError):
            c.build()

    def test_world_coords(self):
        class C(cqparts.Component):
            def __init__(self, *args, **kwargs):
                self._flag_placement_changed = False
                super(C, self).__init__(*args, **kwargs)
            def _placement_changed(self):
                self._flag_placement_changed = True
                super(C, self)._placement_changed()

        c = C()
        self.assertIsNone(c.world_coords)
        cs = CoordSystem.random()
        self.assertFalse(c._flag_placement_changed)
        c.world_coords = cs
        self.assertTrue(c._flag_placement_changed)
        self.assertEquals(c.world_coords, cs)
        c.world_coords = None
        self.assertIsNone(c.world_coords)

    def test_mate_origin(self):
        c = cqparts.Component()
        mate = c.mate_origin
        self.assertEquals(id(mate.component), id(c))
        self.assertEquals(mate.local_coords, CoordSystem())


class MetaclassTests(CQPartsTest):

    def test_base(self):
        self.assertEqual(
            set(cqparts.Component._mate_map.keys()),
            {'origin',}
        )

    def test_inherited(self):
        class A(cqparts.Component):
            @mate
            def foo(self):
                return CoordSystem()
            @mate('bar')
            def _x(self):
                return CoordSystem()

        self.assertEqual(
            set(A._mate_map.keys()),
            {'origin', 'foo', 'bar'}
        )
        self.assertEqual(A._mate_map['foo'], 'foo')
        self.assertEqual(A._mate_map['bar'], '_x')

    def test_inherited_twice(self):
        class A(cqparts.Component):
            @mate
            def foo(self):
                return CoordSystem()
            @mate('bar')
            def _x(self):
                return CoordSystem()

        class B(A):
            @mate
            def bar(self):
                return CoordSystem()
            @mate
            def roo(self):
                return CoordSystem()

        self.assertEqual(
            set(B._mate_map.keys()),
            {'origin', 'foo', 'bar', 'roo'}
        )
        self.assertEqual(B._mate_map['foo'], 'foo')
        self.assertEqual(B._mate_map['bar'], 'bar')
        self.assertEqual(B._mate_map['roo'], 'roo')

    def test_reserved_attribute(self):
        self.assertRaises(ValueError):
            class A(cqparts.Component):
                def _mate_map(self):
                    print("nope!, method name reserved for mapping mates to their functions")
            # instance isn't necessary; metaclass creates the above class
            # and raises the exception.


class ImportExportTests(CodecRegisterTests):

    def test_exporter(self):
        @codec.register_exporter('abc', cqparts.Component)
        class Abc(codec.Exporter):
            pass

        c = cqparts.Component()
        exporter = c.exporter('abc')
        self.assertIsInstance(exporter, Abc)
        self.assertEquals(id(exporter.obj), id(c))

    def test_importer(self):
        @codec.register_importer('abc', cqparts.Component)
        class Abc(codec.Importer):
            pass

        c = cqparts.Component()
        importer = c.importer('abc')
        self.assertIsInstance(importer, Abc)
        self.assertEquals(importer.cls, cqparts.Component)
