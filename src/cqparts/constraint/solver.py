
from ..utils.geometry import CoordSystem
from .base import Constraint

from math import sin, cos, pi, acos, sqrt, atan2
import numpy
from scipy.optimize import least_squares

def get_Rot(alpha, beta, gamma):
    return numpy.array([
        [
            cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma),
            -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma),
            sin(alpha) * sin(beta)
        ],
        [
            sin(alpha) * cos(gamma) + cos(alpha) * cos(beta) * sin(gamma),
            -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma),
            -cos(alpha) * sin(beta)
        ],
        [
            sin(beta) * sin(gamma),
            sin(beta) * cos(gamma),
            cos(beta)
        ]
    ])

def get_index_parameter(x, index):
    return x[index:index+3], x[index+3:index+6]

class NumericSolver:
    def __init__(self, components, constraints, world_coords=CoordSystem()):
        self.constraints = constraints
        self.components = components
        self.world_coords = world_coords

        for constraint in constraints:
            constraint.add_solver(self)

        self.result = None
        self.x = self.get_raw0()

    def get_raw0(self):
        return numpy.zeros(len(self.components) * 6)

    def f(self, x):
        r = [list(c.f(x)) for c in self.constraints]
        return sum(r, [])

    def df(self, x):
        return sum([list(c.df(x)) for c in self.constraints], [])

    def solve(self):
        self.result = least_squares(
            self.f,
            self.x,
            method="dogbox", #method{‘trf’, ‘dogbox’, ‘lm’}
            jac=self.df,
            x_scale="jac",
            verbose=1
        )
        self.x = self.result.x

    def get_coordinates(self):
        coords = []
        for component in self.components:
            index = self.components.index(component) * 6
            offset, angles = get_index_parameter(self.x, index)
            rot = get_Rot(*angles)

            xDir = rot.dot(numpy.array([1, 0, 0]))
            zDir = rot.dot(numpy.array([0, 0, 1]))
            coords.append(
                CoordSystem(
                    list(offset),
                    xDir=list(xDir),
                    normal=list(zDir)
                )
            )
        return coords

def solver(components, constraints, coord_sys=None):
    """
    Solve constraints. Solutions pair :class:`Constraint <cqparts.constraint.Constraint>`
    instances with their suitable :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
    world coordinates.

    :param constraints: constraints to solve
    :type constraints: iterable of :class:`Constraint <cqparts.constraint.Constraint>`
    :param coord_sys: coordinate system to offset solutions (default: no offset)
    :type coord_sys: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`

    :return: generator of (:class:`Component <cqparts.Component>`,
             :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`) tuples.
    """

    if coord_sys is None:
        coord_sys = CoordSystem()  # default

    # Verify list contains constraints
    for constraint in constraints:
        if not isinstance(constraint, Constraint):
            raise ValueError("{!r} is not a constraint".format(constraint))

    solver = NumericSolver(
        list(components.values()),
        constraints,
        coord_sys
    )

    solver.solve()
    return zip(solver.components, solver.get_coordinates())
