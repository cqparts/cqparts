
from base import CQPartsTest
from base import testlabel

# Unit under test
from cqparts.constraint import Mate
from cqparts.constraint import Fixed
from cqparts.constraint import Coincident
from cqparts.utils import CoordSystem

from cqparts.constraint.solver import solver

from partslib.basic import Box


class MateTests(CQPartsTest):

    def test_init(self):
        obj = Box()
        cs = CoordSystem()

        # normal
        m = Mate(obj, cs)
        self.assertEqual(id(m.component), id(obj))
        self.assertEqual(id(m.local_coords), id(cs))

        # no component
        m = Mate(None, cs)
        self.assertIsNone(m.component)
        self.assertEqual(id(m.local_coords), id(cs))

        # no coords
        m = Mate(obj)
        self.assertEqual(id(m.component), id(obj))
        self.assertEqual(m.local_coords, CoordSystem())

    def test_bad_component(self):
        self.assertRaises(TypeError, Mate, 'nope')

    def test_bad_coords(self):
        self.assertRaises(TypeError, Mate, Box(), 123)

    def test_world_coords(self):
        cs1 = CoordSystem(origin=(1,2,3))
        cs2 = CoordSystem(origin=(1,1,1))
        box = Box()
        box.world_coords = cs2
        m = Mate(box, cs1)
        self.assertEqual(m.world_coords, cs1 + cs2)

    def test_world_coords_badcmp(self):
        cs = CoordSystem(origin=(1,2,3))
        box = Box()
        m = Mate(box, cs)
        with self.assertRaises(ValueError):
            m.world_coords

    def test_world_coords_nocmp(self):
        cs = CoordSystem(origin=(1,2,3))
        m = Mate(None, cs)
        self.assertEqual(m.world_coords, cs)

    def test_add_coordsys(self):
        cs1 = CoordSystem(origin=(1,2,3))
        cs2 = CoordSystem(origin=(0,2,4))
        m1 = Mate(Box(), cs1)
        m2 = m1 + cs2
        self.assertEqual(m2.local_coords, cs1 + cs2)

    def test_add_badtype(self):
        m = Mate(Box())
        with self.assertRaises(TypeError):
            m + 100

    def test_repr(self):
        "%r" % Mate(Box(), CoordSystem())

class FixedConstraintTests(CQPartsTest):
    def test_basic(self):
        mate = Mate(Box())
        cs = CoordSystem()

        c = Fixed(mate, cs)
        # assert composition
        self.assertEqual(id(mate), id(c.mate))
        self.assertEqual(cs, c.world_coords)

    def test_bad_mate(self):
        self.assertRaises(TypeError, Fixed, 1)

    def test_bad_coords(self):
        self.assertRaises(TypeError, Fixed, Mate(Box()), 1)

    def test_mate(self):
        mate = Mate(Box())
        cs1 = CoordSystem(origin=(1,1,1))
        box = Box()
        box.world_coords = cs1
        cs2 = CoordSystem(origin=(2,3,4))
        coords = Mate(box, cs2)
        c = Fixed(mate, coords)  # given world_coords is from a mate
        self.assertEqual(cs1 + cs2, c.world_coords)

    def test_default(self):
        c = Fixed(Mate(Box()))
        self.assertEqual(c.world_coords, CoordSystem())


class CoincidentConstraintTests(CQPartsTest):
    def test_basic(self):
        mate1 = Mate(Box())
        mate2 = Mate(Box())
        c = Coincident(mate1, mate2)
        # assert composition
        self.assertEqual(id(mate1), id(c.mate))
        self.assertEqual(id(mate2), id(c.to_mate))

    def test_bad_mate(self):
        self.assertRaises(TypeError, Coincident, 1, Mate(Box()))

    def test_bad_to_mate(self):
        self.assertRaises(TypeError, Coincident, Mate(Box()), 1)
