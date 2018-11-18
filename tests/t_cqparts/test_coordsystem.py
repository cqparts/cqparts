import mock

from base import CQPartsTest
from base import testlabel

from cadquery import Plane, Vector
import cadquery

# Unit under test
from cqparts.utils import CoordSystem


class CoordSystemTests(CQPartsTest):

    @staticmethod
    def mat2list(m, digits=7):
        """Converts cadquery.Matrix to a list"""
        return [
            round(v, digits)
            for v in [
                m.A11, m.A12, m.A13, m.A14,
                m.A21, m.A22, m.A23, m.A24,
                m.A31, m.A32, m.A33, m.A34,
                m.A41, m.A42, m.A43, m.A44
            ]
        ]

    def assertMatrixAlmostEquals(self, first, second, places=6):
        """
        :param first: matrix
        :type first: :class:`cadquery.Matrix`
        :param second: list of 16 numbers (of a 4x4 matrix)
        :type second: :class:`list`
        """
        for (a, b) in zip(self.mat2list(first), second):
            self.assertAlmostEqual(a, b, places=places)

    @staticmethod
    def boundbox2list(bb):
        return [
            bb.xmin, bb.xmax,
            bb.ymin, bb.ymax,
            bb.zmin, bb.zmax,
        ]

    def assertBoundingBoxEquals(self, first, second, places=6):
        """
        :param first: bounding box
        :type first: :class:`cadquery.BoundBox`
        :param second: list of ranges ``[xmin, xmax, ymin, ymax, zmin, zmax]``
        :type second: :class:`list`
        """
        for (a, b) in zip(self.boundbox2list(first), second):
            self.assertAlmostEqual(a, b, places=places)

    def test_from_plane(self):
        plane = Plane(origin=(1,2,3), xDir=(0,1,0), normal=(1,0,0))
        cs = CoordSystem.from_plane(plane)
        self.assertEqual(cs.origin, Vector(1,2,3))
        self.assertEqual(cs.xDir, Vector(0,1,0))
        self.assertEqual(cs.yDir, Vector(0,0,1))
        self.assertEqual(cs.zDir, Vector(1,0,0))

    def test_from_matrix(self):
        from FreeCAD import Matrix

        # identity
        self.assertEqual(
            CoordSystem.from_transform(Matrix()),
            CoordSystem()
        )

        # random #1
        m = Matrix(
            -0.146655,-0.271161,-0.951296,0.0376659,
            -0.676234,0.729359,-0.103649,0.615421,
            0.721942,0.628098,-0.290333,-0.451955,
            0,0,0,1
        )
        cs = CoordSystem.from_transform(m)
        self.assertEqual(cs, CoordSystem(
            origin=(0.0376659, 0.615421, -0.451955),
            xDir=(-0.14665525299526946, -0.6762339076811328, 0.7219417835748246),
            normal=(-0.9512957880009034, -0.10364897690151711, -0.2903329352984416),
        ))

        # random #2
        m = Matrix(
            0.423408,-0.892837,-0.153517,-0.163654,
            -0.617391,-0.408388,0.672345,0.835824,
            -0.662989,-0.189896,-0.724144,0.632804,
            0,0,0,1
        )
        cs = CoordSystem.from_transform(m)
        self.assertEqual(cs, CoordSystem(
            origin=(-0.163654, 0.835824, 0.632804),
            xDir=(0.4234078285564432, -0.6173904937335437, -0.6629892826920875),
            normal=(-0.15351701527110584, 0.672345066881529, -0.7241440720342351),
        ))

    def test_random(self):
        cs = CoordSystem.random()
        self.assertIsInstance(cs, CoordSystem)
        self.assertNotEqual(cs, CoordSystem())  # not an identity matrix
        # (false negative result is possible, but extremely unlikely)

    def test_random_seed(self):
        for i in range(1, 5):
            cs1 = CoordSystem.random(seed=i)
            cs2 = CoordSystem.random(seed=i)  # same seed
            self.assertEqual(cs1, cs2)  # result should be the same

    @mock.patch('random.uniform')
    def test_random_failsafe(self, mock_uniform):
        random_numbers = [
            # 1st try (xDir & normal are parallel; error)
            0, 0, 0, # origin
            1, 0, 0, # xDir
            1, 0, 0, # normal
            # 2nd try (valid data)
            1, 2, 3, # origin
            0, 1, 0, # xDir
            1, 0, 0, # normal
        ]
        mock_uniform.side_effect = random_numbers
        cs = CoordSystem.random()
        self.assertEqual(len(mock_uniform.call_args_list), len(random_numbers))
        self.assertEqual(cs, CoordSystem(
            origin=random_numbers[9:12],
            xDir=random_numbers[12:15],
            normal=random_numbers[15:18],
        ))

    def test_world2local(self):
        # random 1
        cs = CoordSystem(
            origin=(-0.029, -0.222, 0.432),
            xDir=(0.556, -0.719, 0.417),
            normal=(0.779, 0.275, -0.564),
        )
        self.assertMatrixAlmostEquals(
            cs.world_to_local_transform,
            [
                0.55584,-0.719063,0.417122,-0.323709,
                -0.290761,-0.638252,-0.712806,0.157808,
                0.778781,0.274923,-0.563842,0.327197,
                0,0,0,1
            ]
        )

        # random 2
        cs = CoordSystem(
            origin=(-0.654, -0.75, 0.46),
            xDir=(-0.412, 0.906, -0.099),
            normal=(0.474, 0.306, 0.825),
        )
        self.assertMatrixAlmostEquals(
            cs.world_to_local_transform,
            [
                -0.412051,0.905744,-0.0992066,0.455462,
                -0.77801,-0.293074,0.555706,-0.984248,
                0.474252,0.306163,0.825439,0.160081,
                0,0,0,1
            ]
        )

    def test_local2world(self):
        # random 1
        cs = CoordSystem(
            origin=(-0.03, 0.256, -0.246),
            xDir=(-0.018, -0.857, 0.514),
            normal=(-0.868, 0.268, 0.417),
        )
        self.assertMatrixAlmostEquals(
            cs.local_to_world_transform,
            [
                -0.0177607,0.49559,-0.868375,-0.03,
                -0.857519,0.439062,0.268116,0.256,
                0.514146,0.74941,0.41718,-0.246,
                -0,0,0,1,
            ]
        )

        # random 2
        cs = CoordSystem(
            origin=(-0.539, -0.071, -0.17),
            xDir=(0.866, -0.189, -0.463),
            normal=(-0.468, -0.632, -0.618),
        )
        self.assertMatrixAlmostEquals(
            cs.local_to_world_transform,
            [
                0.866118,0.175777,-0.467913,-0.539,
                -0.18881,-0.751715,-0.631882,-0.071,
                -0.462808,0.635631,-0.617885,-0.17,
                0,-0,0,1,
            ]
        )

    def test_arithmetic_add_coordsys(self):
        # random 1
        cs = CoordSystem(
            origin=(0.319872,-0.424248,-0.813118),
            xDir=(0.301597,0.844131,-0.443263),
            normal=(0.518197,-0.535377,-0.666966),
        )
        cs_add = CoordSystem(
            origin=(-0.965988,0.438111,0.447495),
            xDir=(-0.903357,0.322463,-0.282777),
            normal=(0.0176109,-0.630881,-0.77568),
        )
        self.assertEqual(
            cs + cs_add,
            CoordSystem(
                origin=(0.6110520112439473, -1.4667419254474168, -0.42101284070314754),
                xDir=(-0.16091098866905712, -0.6019554630954405, 0.7821491380645386),
                normal=(-0.901549677957146, 0.41213999099584614, 0.13171486627298448),
            )
        )

        # random 2
        cs = CoordSystem(
            origin=(0.997758,-0.429350,0.469693),
            xDir=(-0.949669,0.304061,-0.0753356),
            normal=(-0.265922,-0.655403,0.706917),
        )
        cs_add = CoordSystem(
            origin=(0.604043,-0.918366,0.765700),
            xDir=(-0.208045,0.778042,0.592762),
            normal=(0.591826,-0.382369,0.709603),
        )
        self.assertEqual(
            cs + cs_add,
            CoordSystem(
                origin=(0.3725549528751452, -0.1125950462339067, 1.6113356739288598),
                xDir=(-0.08887557530345871, -0.9896725888680419, -0.11246910223571256),
                normal=(-0.6874287881318142, -0.020766321770180177, 0.7259548340825087),
            )
        )

    def test_arithmetic_add_vector(self):
        # random 1
        cs = CoordSystem(
            origin=(0.776696,-0.155044,0.464622),
            xDir=(-0.792263,-0.141302,0.593594),
            normal=(-0.586401,-0.0926133,-0.804709),
        )
        v = Vector(0.894579,-0.282728,-0.428593)
        self.assertEqual(
            cs + v,
            Vector(0.3669727263895199, -0.5204201245493684, 1.3378492301899407)
        )

        # random 2
        cs = CoordSystem(
            origin=(-0.370354,-0.146263,-0.007179),
            xDir=(-0.96932,0.182199,-0.16499),
            normal=(0.244193,0.790464,-0.561726),
        )
        v = Vector(-0.111398,-0.465007,-0.221905)
        self.assertEqual(
            cs + v,
            Vector(-0.3035072972382829, -0.613895258440105, -0.2411329328032198)
        )

    def test_arithmetic_add_workplane(self):
        # random 1
        cs = CoordSystem(
            origin=(-0.572012,0.137190,-0.927598),
            xDir=(0.877633,0.381758,0.289866),
            normal=(-0.465231,0.824021,0.32334),
        )
        obj = cadquery.Workplane('XY').box(1,1,1)  # unit cube
        self.assertBoundingBoxEquals(
            (cs + obj).val().BoundingBox(),
            [
                -1.3011527973859502, 0.15712879738595031,
                -0.6750138361946009, 0.9493938361946012,
                -1.6845977586686152, -0.1705982413313848,
            ]
        )

        # random 2
        cs = CoordSystem(
            origin=(0.092874,0.472599,0.277811),
            xDir=(0.559151,0.828735,-0.0234319),
            normal=(0.399938,-0.244868,0.883227),
        )
        obj = cadquery.Workplane('XY').box(1,1,1)  # unit cube
        self.assertBoundingBoxEquals(
            (cs + obj).val().BoundingBox(),
            [
                -0.7497819487047321, 0.9355299487047323,
                -0.31581638155097225, 1.261014381550972,
                -0.4096982706849824, 0.9653202706849824,
            ]
        )

    def test_arithmetic_add_bad_type(self):
        with self.assertRaises(TypeError):
            CoordSystem.random() + 1
        with self.assertRaises(TypeError):
            CoordSystem.random() + 'bad_type'
        with self.assertRaises(TypeError):
            CoordSystem.random() + None

    def test_arithmetic_sub_coordsys(self):
        # random 1
        cs = CoordSystem(
            origin=(0.995014,0.597397,0.251518),
            xDir=(-0.701536,-0.665758,0.254191),
            normal=(0.135645,0.225422,0.964772),
        )
        cs_sub = CoordSystem(
            origin=(-0.320574,0.951257,0.176344),
            xDir=(-0.744255,-0.650638,-0.150844),
            normal=(0.419232,-0.279276,-0.863858),
        )
        self.assertEqual(
            cs - cs_sub,
            CoordSystem(
                origin=(-0.7602379451931977, -0.9700309903527986, 0.5854211817688126),
                xDir=(0.9169464676048765, -0.22755650176590822, -0.32776090988859785),
                normal=(-0.39315299213245875, -0.37502955527701604, -0.8395138816279446),
            )
        )

        # random 2
        cs = CoordSystem(
            origin=(-0.980361,0.591789,-0.073316),
            xDir=(-0.27988,-0.085973,-0.956178),
            normal=(0.755724,0.59451,-0.27466),
        )
        cs_sub = CoordSystem(
            origin=(0.480657,0.627596,0.409464),
            xDir=(-0.0929824,-0.728202,0.679026),
            normal=(0.549731,0.531063,0.644801),
        )
        self.assertEqual(
            cs - cs_sub,
            CoordSystem(
                origin=(-0.1658962438630106, -1.02792754287956, -1.133479452321362),
                xDir=(-0.5606397275073202, 0.1404609281661355, -0.8160599387295184),
                normal=(-0.6896940658874535, 0.466189492307297, 0.5540662891224277),
            )
        )

    def test_arithmetic_sub_bad_type(self):
        with self.assertRaises(TypeError):
            CoordSystem.random() - 1
        with self.assertRaises(TypeError):
            CoordSystem.random() - 'bad_type'
        with self.assertRaises(TypeError):
            CoordSystem.random() - None
        obj = cadquery.Workplane('XY').box(1, 1, 1)
        with self.assertRaises(TypeError):
            CoordSystem.random() - obj
        v = Vector(1, 2, 3)
        with self.assertRaises(TypeError):
            CoordSystem.random() - v

    def test_repr(self):
        repr_str = repr(CoordSystem.random())
        self.assertIsInstance(repr_str, str)
        self.assertTrue(bool(repr_str))
