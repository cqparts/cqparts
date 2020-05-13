
from base import CQPartsTest
from base import testlabel

import cadquery

# Unit under test
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem
from cqparts.constraint.solver import solver

from partslib.basic import Box


class FixedSolverTests(CQPartsTest):

    def test_random(self):
        box = Box()

        for (s1, s2) in [(1, 2), (3, 4), (5, 6), (7, 8)]:
            cs1 = CoordSystem.random(seed=s1)
            # random CoordSystem is not orthogonal
            cs1.xDir = cs1.yDir.cross(cs1.zDir)
            cs2 = CoordSystem.random(seed=s2)
            # random CoordSystem is not orthogonal
            cs2.xDir = cs2.yDir.cross(cs2.zDir)

            # create constraint
            c = Fixed(Mate(box, cs1), cs2)
            # solve
            solution = list(solver({"box": box}, [c]))
            # assert results
            self.assertEqual(len(solution), 1)
            (part, coords) = solution[0]
            self.assertEqual(id(part), id(box))
            self.assertEqual(coords, cs2 + (CoordSystem() - cs1))
            # note: the above test is effectively reverse engineering the solution.
            #       only (partially) effective as a regression test

    def test_rotation(self):
        box = Box()

        # +'ve rotation
        c = Fixed(Mate(box, CoordSystem()), CoordSystem(xDir=(1, 0.1, 0)))
        (part, coords) = list(solver({"box": box}, [c]))[0]
        self.assertEqual(coords.origin, cadquery.Vector())
        self.assertEqual(coords.xDir, cadquery.Vector(1, 0.1, 0).normalized())
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

        # -'ve rotation
        c = Fixed(Mate(box, CoordSystem(xDir=(1, 0.1, 0))), CoordSystem())
        (part, coords) = list(solver({"box": box}, [c]))[0]
        self.assertEqual(coords.origin, cadquery.Vector())
        self.assertEqual(coords.xDir, cadquery.Vector(1, -0.1, 0).normalized())
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

    def test_translation(self):
        box = Box()

        # +'ve translation
        c = Fixed(Mate(box, CoordSystem()), CoordSystem(origin=(1, 2, 3)))
        (part, coords) = list(solver({"box": box}, [c]))[0]
        self.assertEqual(coords.origin, cadquery.Vector(1, 2, 3))
        self.assertEqual(coords.xDir, cadquery.Vector(1, 0, 0))
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

        # -'ve translation
        c = Fixed(Mate(box, CoordSystem(origin=(1, 2, 3))), CoordSystem())
        (part, coords) = list(solver({"box": box}, [c]))[0]
        self.assertEqual(coords.origin, cadquery.Vector(-1, -2, -3))
        self.assertEqual(coords.xDir, cadquery.Vector(1, 0, 0))
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

    def test_origin(self):
        box = Box()
        c = Fixed(Mate(box), CoordSystem())

        # default origin (0, 0, 0)
        (part, coords) = list(solver({"box": box}, [c]))[0]
        self.assertEqual(coords, CoordSystem((0, 0, 0)))

        # origin displaced
        (part, coords) = list(solver({"box": box}, [c], CoordSystem(origin=(1, 2, 3))))[0]
        self.assertEqual(coords, CoordSystem((1, 2, 3)))


class CoincidentSolverTests(CQPartsTest):

    # New solver always returns a result.
    # Test "test_no_solution" doesn't make sense for it.

    def test_solution(self):
        (box1, box2) = (Box(), Box())
        # set box1 world location: sit it on top of xy plane
        c1 = Fixed(box1.mate_origin, CoordSystem((0, 0, box1.height / 2)))

        # +'ve rotation
        c2 = Coincident(box2.mate_origin, box1.mate_top)
        solution = list(solver({"box1": box1, "box2": box2}, [c1, c2]))
        self.assertEqual(len(solution), 2)
        (part, coords) = solution[1]
        self.assertEqual(id(part), id(box2))
        self.assertEqual(coords, CoordSystem((0, 0, box1.height)))

    def test_rotation(self):
        (box1, box2) = (Box(), Box())
        # set box1 world location: sit it on top of xy plane
        c1 = Fixed(box1.mate_origin, CoordSystem((0, 0, box1.height / 2)))

        # +'ve rotation
        c2 = Coincident(
            box2.mate_origin,
            box1.mate_top + CoordSystem(xDir=(1, 0.1, 0))
        )
        results = list(solver({"box1": box1, "box2": box2}, [c1, c2]))
        (part, coords) = results[1]
        self.assertEqual(coords.origin, cadquery.Vector(0, 0, box1.height))
        self.assertEqual(coords.xDir, cadquery.Vector(1, 0.1, 0).normalized())
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

        # -'ve rotation
        c2 = Coincident(
            box2.mate_origin + CoordSystem(xDir=(1, 0.1, 0)),
            box1.mate_top
        )
        results = list(solver({"box1": box1, "box2": box2}, [c1, c2]))
        (part, coords) = results[1]
        self.assertEqual(coords.origin, cadquery.Vector(0, 0, box1.height))
        self.assertEqual(coords.xDir, cadquery.Vector(1, -0.1, 0).normalized())
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

    def test_translation(self):
        (box1, box2) = (Box(), Box())
        # set box1 world location: sit it on top of xy plane
        c1 = Fixed(box1.mate_origin, CoordSystem((0, 0, box1.height / 2)))

        # +'ve translation
        c2 = Coincident(
            box2.mate_origin,
            box1.mate_top + CoordSystem(origin=(1, 2, 3))
        )
        results = list(solver({"box1": box1, "box2": box2}, [c1, c2]))
        (part, coords) = results[1]
        self.assertEqual(coords.origin, cadquery.Vector(1, 2, 3 + box1.height))
        self.assertEqual(coords.xDir, cadquery.Vector(1, 0, 0))
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))

        # -'ve translation
        c2 = Coincident(
            box2.mate_origin + CoordSystem(origin=(1, 2, 3)),
            box1.mate_top
        )
        results = list(solver({"box1": box1, "box2": box2}, [c1, c2]))
        (part, coords) = results[1]
        self.assertEqual(coords.origin, cadquery.Vector(-1, -2, -3 + box1.height))
        self.assertEqual(coords.xDir, cadquery.Vector(1, 0, 0))
        self.assertEqual(coords.zDir, cadquery.Vector(0, 0, 1))


class SolverOrderTests(CQPartsTest):

    # ------ Fixed & Coincident ------
    # Fixed, Coincident
    def test_coincident_forward(self):
        (box1, box2) = (Box(), Box())
        constraints = [  # stack box2 on box1
            Fixed(box1.mate_bottom, CoordSystem()),
            Coincident(box2.mate_bottom, box1.mate_top),
        ]
        solution = solver({"box1": box1, "box2": box2}, constraints)

        # 1st solution : box1
        (part, coords) = next(solution)
        self.assertEqual(id(part), id(box1))

        part.world_coords = coords

        # 2nd solution : box2
        (part, coords) = next(solution)
        self.assertEqual(id(part), id(box2))

        with self.assertRaises(StopIteration):
            next(solution)

    # Coincident, Fixed
    def test_coincident_backward(self):
        (box1, box2) = (Box(), Box())
        constraints = [  # stack box2 on box1 (in reversed logical order)
            Coincident(box2.mate_bottom, box1.mate_top),
            Fixed(box1.mate_bottom, CoordSystem()),
        ]
        solution = solver({"box1": box1, "box2": box2}, constraints)

        # 1st solution : box1
        (part, coords) = next(solution)
        self.assertEqual(id(part), id(box1))

        part.world_coords = coords

        # 2nd solution : box2
        (part, coords) = next(solution)
        self.assertEqual(id(part), id(box2))

        with self.assertRaises(StopIteration):
            next(solution)


class BadSolverTests(CQPartsTest):

    def test_non_constraint(self):
        with self.assertRaises(ValueError):
            list(solver({}, ['not_a_constraint']))
