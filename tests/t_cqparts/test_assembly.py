import re

from base import CQPartsTest
from base import testlabel

from partslib import Box, Cylinder, CubeStack, SimpleCar
from partslib import simplecar

# Unit under test
import cqparts
from cqparts.constraint import Fixed, Coincident
from cqparts.utils import CoordSystem
from cqparts.errors import AssemblyFindError


class BadAssemblyTests(CQPartsTest):

    # pre-mature assembiles
    def test_no_make_components(self):
        class A(cqparts.Assembly):
            pass

        with self.assertRaises(NotImplementedError):
            A().components

    def test_no_make_constraints(self):
        class A(cqparts.Assembly):
            def make_components(self):
                return {'p': Box()}

        with self.assertRaises(NotImplementedError):
            A().components

    # bad returns
    def test_bad_component_return(self):
        class A(cqparts.Assembly):
            def make_components(self):
                return 123

        with self.assertRaises(TypeError):
            A().components

    def test_bad_component_yield(self):
        class A(cqparts.Assembly):
            def make_components(self):
                yield 123

        with self.assertRaises(TypeError):
            A().components

    def test_bad_component_value(self):
        class A(cqparts.Assembly):
            def make_components(self):
                yield {
                    'p': Box(),  # good component
                    'x': 123,  # bad component
                }

        with self.assertRaises(ValueError):
            A().components

    def test_bad_component_key(self):
        class A(cqparts.Assembly):
            def make_components(self):
                yield {
                    'p': Box(),  # good key
                    1: Box(),  # bad key (must be a string)
                }

        with self.assertRaises(ValueError):
            A().components

    def test_bad_component_keychar(self):
        class A(cqparts.Assembly):
            def make_components(self):
                yield {
                    'p': Box(),  # good key
                    'a.b': Box(),  # key can't contain a '.'
                }

        with self.assertRaises(ValueError):
            A().components

    def test_bad_constraint_return(self):
        class A(cqparts.Assembly):
            def make_components(self):
                return {'p': Box()}
            def make_constraints(self):
                return 123

        with self.assertRaises(TypeError):
            A().components

    def test_bad_constraint_yield(self):
        class A(cqparts.Assembly):
            def make_components(self):
                return {'p': Box()}
            def make_constraints(self):
                yield 123

        with self.assertRaises(TypeError):
            A().components

    def test_bad_constraint_value(self):
        class A(cqparts.Assembly):
            def make_components(self):
                return {'p': Box()}
            def make_constraints(self):
                return [
                    Fixed(self.components['p'].mate_origin),  # good value
                    123,  # bad value
                ]

        with self.assertRaises(ValueError):
            A().components


class BuildCycleTests(CQPartsTest):

    def test_standard(self):
        # Define test components
        class P(Box):
            def __init__(self, *args, **kwargs):
                self._built = False
                super(P, self).__init__(*args, **kwargs)
            def make(self):
                self._built = True
                return super(P, self).make()

        class A(cqparts.Assembly):
            def __init__(self, *args, **kwargs):
                self._flags = []
                super(A, self).__init__(*args, **kwargs)
            def build(self, *args, **kwargs):
                self._flags.append('build')
                return super(A, self).build(*args, **kwargs)
            def make_components(self):
                self._flags.append('cmp')
                return {'p1': P(), 'p2': P()}
            def make_constraints(self):
                self._flags.append('con')
                (p1, p2) = (self.components['p1'], self.components['p2'])
                return [
                    Fixed(p1.mate_origin),
                    Coincident(p2.mate_bottom, p1.mate_top),
                ]

        # .components
        asm = A()
        self.assertEqual(asm._flags, [])
        asm.components  # key stimulus
        self.assertEqual(asm._flags, ['build', 'cmp', 'con'])
        for name in ['p1', 'p2']:
            self.assertIsNotNone(asm.components[name].world_coords)
            self.assertFalse(asm.components[name]._built)

        # Build
        asm = A()
        asm.build(recursive=False)  # key stimulus
        self.assertEqual(asm._flags, ['build', 'cmp', 'con'])
        for name in ['p1', 'p2']:
            self.assertIsNotNone(asm.components[name].world_coords)
            self.assertFalse(asm.components[name]._built)

        # Build Recursively
        asm = A()
        asm.build(recursive=True)  # key stimulus
        self.assertEqual(asm._flags, ['build', 'cmp', 'con'])
        for name in ['p1', 'p2']:
            self.assertIsNotNone(asm.components[name].world_coords)
            self.assertTrue(asm.components[name]._built)  # True

    def test_multi_pass(self):
        class P(Box):
            def __init__(self, *args, **kwargs):
                self._built = False
                super(P, self).__init__(*args, **kwargs)
            def make(self):
                self._built = True
                return super(P, self).make()

        class A(cqparts.Assembly):
            def __init__(self, *args, **kwargs):
                self._flags = []
                super(A, self).__init__(*args, **kwargs)
            def build(self, *args, **kwargs):
                self._flags.append('build')
                return super(A, self).build(*args, **kwargs)
            def make_components(self):
                self._flags.append('cmp1')
                yield {'p1': P()}
                self._flags.append('cmp2')
                yield {'p2': P()}
                self._flags.append('cmp3')
            def make_constraints(self):
                self._flags.append('con1')
                p1 = self.components['p1']
                yield [Fixed(p1.mate_origin)]
                self._flags.append('con2')
                p2 = self.components['p2']
                yield [Coincident(p2.mate_bottom, p1.mate_top)]
                self._flags.append('con3')
            def solve(self, *args, **kwargs):
                self._flags.append('solve')
                return super(A, self).solve(*args, **kwargs)

        expected_flag_order = [
            'build',
            'cmp1', 'con1', 'solve',  # 1st pass
            'cmp2', 'con2', 'solve',  # 2nd pass
            'cmp3', 'con3',  # final pass, nothing yielded
        ]

        # .components
        asm = A()
        self.assertEqual(asm._flags, [])
        asm.components
        self.assertEqual(asm._flags, expected_flag_order)
        for name in ['p1', 'p2']:
            self.assertIsNotNone(asm.components[name].world_coords)
            self.assertFalse(asm.components[name]._built)

        # Build
        asm = A()
        asm.build(recursive=False)  # key stimulus
        self.assertEqual(asm._flags, expected_flag_order)
        for name in ['p1', 'p2']:
            self.assertIsNotNone(asm.components[name].world_coords)
            self.assertFalse(asm.components[name]._built)

        # Build Recursively
        asm = A()
        asm.build(recursive=True)  # key stimulus
        self.assertEqual(asm._flags, expected_flag_order)
        for name in ['p1', 'p2']:
            self.assertIsNotNone(asm.components[name].world_coords)
            self.assertTrue(asm.components[name]._built)  # True


class TreeStringTests(CQPartsTest):

    def test_one_layer(self):
        obj = CubeStack()
        tree_str = obj.tree_str(name='cubestack')
        self.assertEqual(tree_str, '\n'.join([
            u"cubestack",
            u" \u251c\u25cb cube_a",
            u" \u2514\u25cb cube_b\n",
        ]))

    def test_two_layer(self):
        obj = SimpleCar()
        tree_str = obj.tree_str(name='car')
        self.assertEqual(tree_str, '\n'.join([
            u"car",
            u" \u251c\u2500 back_wheels",
            u" \u2502   \u251c\u25cb axle",
            u" \u2502   \u251c\u25cb wheel_left",
            u" \u2502   \u2514\u25cb wheel_right",
            u" \u251c\u25cb chassis",
            u" \u2514\u2500 front_wheels",
            u"     \u251c\u25cb axle",
            u"     \u251c\u25cb wheel_left",
            u"     \u2514\u25cb wheel_right\n",
        ]))

    def test_prefix(self):
        obj = CubeStack()
        tree_str = obj.tree_str(name='cubestack', prefix="--")
        self.assertEqual(tree_str, '\n'.join([
            u"--cubestack",
            u"-- \u251c\u25cb cube_a",
            u"-- \u2514\u25cb cube_b\n",
        ]))

    def test_repr(self):
        obj = CubeStack()
        # no repr
        tree_str = obj.tree_str(name='cubestack', add_repr=False)
        for line in tree_str.rstrip('\n').split('\n'):
            self.assertIsNone(re.search(r'<[^>]+>', line))

        # repr on each line
        tree_str = obj.tree_str(name='cubestack', add_repr=True)
        for line in tree_str.rstrip('\n').split('\n'):
            self.assertIsNotNone(re.search(r'<[^>]+>', line))

        # repeat: nested obj
        obj = SimpleCar()
        tree_str = obj.tree_str(name='car', add_repr=True)
        for line in tree_str.rstrip('\n').split('\n'):
            self.assertIsNotNone(re.search(r'<[^>]+>', line))


class SearchTests(CQPartsTest):

    def test_1st_layer(self):
        car = SimpleCar()
        self.assertIsInstance(car.find('chassis'), simplecar.Chassis)  # part
        self.assertIsInstance(car.find('front_wheels'), simplecar.AxleAsm)  # assembly

    def test_2nd_layer(self):
        car = SimpleCar()
        self.assertIsInstance(car.find('front_wheels.axle'), simplecar.Axle)
        self.assertIsInstance(car.find('front_wheels.wheel_left'), simplecar.Wheel)

    def test_bad_paths(self):
        car = SimpleCar()
        bad_search_keys = [
            'nope',  # 1st layer part doesn't exist
            'chassis.foo',  # part doesn't have components
            'front_wheels.no_exist',  # asm component doesn't exist
            'front_wheels.axle.no_exist',  # part has no components
        ]
        for search_key in bad_search_keys:
            with self.assertRaises(AssemblyFindError):
                car.find(search_key)
