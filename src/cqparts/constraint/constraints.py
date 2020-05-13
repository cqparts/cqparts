
from .base import Constraint
from .mate import Mate
from ..utils.geometry import CoordSystem


import numpy
from math import sin, cos, pi, acos, sqrt, atan2
from itertools import chain
from scipy.optimize import least_squares, Bounds

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

def get_Rot_dalpha(alpha, beta, gamma):
    return numpy.array([
        [
            -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma),
            sin(alpha) * sin(gamma) - cos(alpha) * cos(beta) * cos(gamma),
            cos(alpha) * sin(beta)
        ],
        [
            cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma),
            -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma),
            sin(alpha) * sin(beta)
        ],
        [
            0,
            0,
            0
        ]
    ])

def get_Rot_dbeta(alpha, beta, gamma):
    return numpy.array([
        [
            sin(alpha) * sin(beta) * sin(gamma),
            sin(alpha) * sin(beta) * cos(gamma),
            sin(alpha) * cos(beta)
        ],
        [
            -cos(alpha) * sin(beta) * sin(gamma),
            -cos(alpha) * sin(beta) * cos(gamma),
            -cos(alpha) * cos(beta)
        ],
        [
            cos(beta) * sin(gamma),
            cos(beta) * cos(gamma),
            -sin(beta)
        ]
    ])

def get_Rot_dgamma(alpha, beta, gamma):
    return numpy.array([
        [
            -cos(alpha) * sin(gamma) - sin(alpha) * cos(beta) * cos(gamma),
            -cos(alpha) * cos(gamma) + sin(alpha) * cos(beta) * sin(gamma),
            0
        ],
        [
            -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma),
            -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma),
            0
        ],
        [
            sin(beta) * cos(gamma),
            -sin(beta) * sin(gamma),
            0
        ]
    ])

def get_index_parameter(x, index):
    return x[index:index+3], x[index+3:index+6]

class Plane(Constraint):
    def __init__(self, mate1, mate2, distance=0):
        self.mate1 = mate1
        self.mate2 = mate2

        self.l1o = mate1.local_coords.origin.toTuple()
        self.l2o = mate2.local_coords.origin.toTuple()
        self.l2z = mate2.local_coords.zDir.toTuple()
        self.distance = distance

    def add_solver(self, solver):
        self.solver = solver
        self.i1 = solver.components.index(self.mate1.component) * 6
        self.i2 = solver.components.index(self.mate2.component) * 6

    def f(self, x):
        p1o, p1e = get_index_parameter(x, self.i1)
        p2o, p2e = get_index_parameter(x, self.i2)

        rot1 = get_Rot(*p1e)
        rot2 = get_Rot(*p2e)

        l1o = rot1.dot(self.l1o)
        l2o = rot2.dot(self.l2o)
        l2z = rot2.dot(self.l2z)

        # (x - p) * n = 0
        ret = (p1o + l1o - p2o - l2o - self.distance * l2z).dot(l2z)

        return [ret]

    def df(self, x):
        p1o, p1e = get_index_parameter(x, self.i1)
        p2o, p2e = get_index_parameter(x, self.i2)

        rot1 = get_Rot(*p1e)
        rot2 = get_Rot(*p2e)

        l1o = rot1.dot(self.l1o)
        l2o = rot2.dot(self.l2o)
        l2z = rot2.dot(self.l2z)

        m = p1o + l1o - p2o - l2o - self.distance * l2z

        ret = numpy.zeros((1, len(x)))
        ret[:, self.i1+0:self.i1+3] = l2z
        ret[:, self.i1+3] = get_Rot_dalpha(*p1e).dot(self.l1o).dot(l2z)
        ret[:, self.i1+4] = get_Rot_dbeta(*p1e).dot(self.l1o).dot(l2z)
        ret[:, self.i1+5] = get_Rot_dgamma(*p1e).dot(self.l1o).dot(l2z)

        ret[:, self.i2+0:self.i2+3] = -l2z
        ret[:, self.i2+3] = (-get_Rot_dalpha(*p2e).dot(self.l2o) -
                             self.distance * get_Rot_dalpha(*p2e).dot(self.l2z)).dot(l2z) + \
                            m.dot(get_Rot_dalpha(*p2e).dot(self.l2z))
        ret[:, self.i2+4] = (-get_Rot_dbeta(*p2e).dot(self.l2o) -
                             self.distance * get_Rot_dbeta(*p2e).dot(self.l2z)).dot(l2z) + \
                            m.dot(get_Rot_dbeta(*p2e).dot(self.l2z))
        ret[:, self.i2+5] = (-get_Rot_dgamma(*p2e).dot(self.l2o) -
                             self.distance * get_Rot_dgamma(*p2e).dot(self.l2z)).dot(l2z) + \
                            m.dot(get_Rot_dgamma(*p2e).dot(self.l2z))

        return list(ret)


class Direction(Constraint):
    """
    Set a component's world coordinates of ``mate.component`` so that
    they have the same orientation than the ``to_mate.world_coords``.

    """
    def __init__(self, mate, to_mate, rotation=(0, 0, 0)):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param to_mate: mate to lock ``mate`` to
        :type to_mate: :class:`Mate <cqparts.constraint.Mate>`
        :param rotation: rotation of the mate
        :type rotation: (X degree, Y degree, Z degree)
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # to_mate
        if isinstance(to_mate, Mate):
            self.to_mate = to_mate
        else:
            raise TypeError("to_mate must be a %r, not a %r" % (Mate, type(to_mate)))

        l1 = self.mate.local_coords.rotated(rotation)
        l2 = self.to_mate.local_coords
        self.l1x = l1.xDir.toTuple()
        self.l1z = l1.zDir.toTuple()
        self.l2x = l2.xDir.toTuple()
        self.l2z = l2.zDir.toTuple()

    def add_solver(self, solver):
        self.solver = solver
        self.i1 = solver.components.index(self.mate.component) * 6
        self.i2 = solver.components.index(self.to_mate.component) * 6

    def f(self, x):
        _, p1e = get_index_parameter(x, self.i1)
        _, p2e = get_index_parameter(x, self.i2)

        rot1 = get_Rot(*p1e)
        rot2 = get_Rot(*p2e)

        mx = rot1.dot(self.l1x) - rot2.dot(self.l2x)
        mz = rot1.dot(self.l1z) - rot2.dot(self.l2z)

        return list(mx) + list(mz)

    def df(self, x):
        _, p1e = get_index_parameter(x, self.i1)
        _, p2e = get_index_parameter(x, self.i2)

        retx = numpy.zeros((3, len(x)))
        retx[:, self.i1+3] = get_Rot_dalpha(*p1e).dot(self.l1x)
        retx[:, self.i1+4] = get_Rot_dbeta(*p1e).dot(self.l1x)
        retx[:, self.i1+5] = get_Rot_dgamma(*p1e).dot(self.l1x)

        retx[:, self.i2+3] = -get_Rot_dalpha(*p2e).dot(self.l2x)
        retx[:, self.i2+4] = -get_Rot_dbeta(*p2e).dot(self.l2x)
        retx[:, self.i2+5] = -get_Rot_dgamma(*p2e).dot(self.l2x)

        retz = numpy.zeros((3, len(x)))
        retz[:, self.i1+3] = get_Rot_dalpha(*p1e).dot(self.l1z)
        retz[:, self.i1+4] = get_Rot_dbeta(*p1e).dot(self.l1z)
        retz[:, self.i1+5] = get_Rot_dgamma(*p1e).dot(self.l1z)

        retz[:, self.i2+3] = -get_Rot_dalpha(*p2e).dot(self.l2z)
        retz[:, self.i2+4] = -get_Rot_dbeta(*p2e).dot(self.l2z)
        retz[:, self.i2+5] = -get_Rot_dgamma(*p2e).dot(self.l2z)

        return list(retx) + list(retz)


class Position(Constraint):
    """
    Set a component's world coordinates of ``mate.component`` so that
    both origins are at the same position:
    ``mate.world_coords.origin`` == ``to_mate.world_coords.origin``.

    """
    def __init__(self, mate, to_mate):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param to_mate: mate to lock ``mate`` to
        :type to_mate: :class:`Mate <cqparts.constraint.Mate>`
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # to_mate
        if isinstance(to_mate, Mate):
            self.to_mate = to_mate
        else:
            raise TypeError("to_mate must be a %r, not a %r" % (Mate, type(to_mate)))

        self.l1o = self.mate.local_coords.origin.toTuple()
        self.l2o = self.to_mate.local_coords.origin.toTuple()

    def add_solver(self, solver):
        self.solver = solver
        self.i1 = solver.components.index(self.mate.component) * 6
        self.i2 = solver.components.index(self.to_mate.component) * 6

    def f(self, x):
        p1o, p1e = get_index_parameter(x, self.i1)
        p2o, p2e = get_index_parameter(x, self.i2)

        rot1 = get_Rot(*p1e)
        rot2 = get_Rot(*p2e)

        l1o = rot1.dot(self.l1o)
        l2o = rot2.dot(self.l2o)

        m = (p1o + l1o - p2o - l2o)

        return m

    def df(self, x):
        _, p1e = get_index_parameter(x, self.i1)
        _, p2e = get_index_parameter(x, self.i2)

        ret = numpy.zeros((3, len(x)))
        ret[:, self.i1:self.i1+3] = numpy.eye(3)

        ret[:, self.i1+3] = get_Rot_dalpha(*p1e).dot(self.l1o)
        ret[:, self.i1+4] = get_Rot_dbeta(*p1e).dot(self.l1o)
        ret[:, self.i1+5] = get_Rot_dgamma(*p1e).dot(self.l1o)

        ret[:, self.i2:self.i2+3] = -numpy.eye(3)

        ret[:, self.i2+3] = -get_Rot_dalpha(*p2e).dot(self.l2o)
        ret[:, self.i2+4] = -get_Rot_dbeta(*p2e).dot(self.l2o)
        ret[:, self.i2+5] = -get_Rot_dgamma(*p2e).dot(self.l2o)

        return ret


class Coincident(Constraint):
    """
    Set a component's world coordinates of ``mate.component`` so that
    both have the same position and orientation:
    ``mate.world_coords`` == ``to_mate.world_coords``.

    """
    def __init__(self, mate, to_mate, rotation=(0, 0, 0)):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param to_mate: mate to lock ``mate`` to
        :type to_mate: :class:`Mate <cqparts.constraint.Mate>`
        :param rotation: rotation of the mate
        :type rotation: (X degree, Y degree, Z degree)
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # to_mate
        if isinstance(to_mate, Mate):
            self.to_mate = to_mate
        else:
            raise TypeError("to_mate must be a %r, not a %r" % (Mate, type(to_mate)))

        self.position = Position(mate, to_mate)
        self.direction = Direction(mate, to_mate, rotation)

    def add_solver(self, solver):
        self.position.add_solver(solver)
        self.direction.add_solver(solver)

    def f(self, x):
        return list(self.position.f(x)) + list(self.direction.f(x))

    def df(self, x):
        return list(self.position.df(x)) + list(self.direction.df(x))


class FixedPosition(Constraint):
    """
    Sets a component's world coordinates so the given ``mate`` is
    positioned to the given ``world_coords``.
    """

    def __init__(self, mate, world_coords=None):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param world_coords: world coordinates to lock ``mate`` to
        :type world_coords: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :raises TypeError: if an invalid parameter type is passed

        If the ``world_coords`` parameter is set as a
        :class:`Mate <cqparts.constraint.Mate>` instance, the mate's
        ``.world_coords`` is used.

        If ``world_coords`` is ``None``, the object is locked to the origin.
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # world_coords
        if isinstance(world_coords, CoordSystem):
            self.world_coords = world_coords
        elif isinstance(world_coords, Mate):
            self.world_coords = world_coords.world_coords
        elif world_coords is None:
            self.world_coords = CoordSystem()
        else:
            raise TypeError(
                "world_coords must be a %r or %r, not a %r" % (Mate, CoordSystem, type(world_coords))
            )

        self.l1o = self.mate.local_coords.origin.toTuple()

    def add_solver(self, solver):
        self.solver = solver
        self.index = solver.components.index(self.mate.component) * 6
        # Adding solver world_coords for compatibility reasons
        target_coords = self.world_coords + solver.world_coords

        self.offset = numpy.array(target_coords.origin.toTuple())
        self.zDir = numpy.array(target_coords.zDir.toTuple())
        self.xDir = numpy.array(target_coords.xDir.toTuple())

    def f(self, x):
        p1o, p1e = get_index_parameter(x, self.index)

        rot = get_Rot(*p1e)
        l1o = rot.dot(self.l1o)

        ro = p1o + l1o - self.offset

        return list(ro)

    def df(self, x):
        _, p1e = get_index_parameter(x, self.i1)

        ret = numpy.zeros((3, len(x)))
        ret[:, self.i1:self.i1+3] = numpy.eye(3)

        ret[:, self.i1+3] = get_Rot_dalpha(*p1e).dot(self.l1o)
        ret[:, self.i1+4] = get_Rot_dbeta(*p1e).dot(self.l1o)
        ret[:, self.i1+5] = get_Rot_dgamma(*p1e).dot(self.l1o)

        return ret

    def df(self, x):
        _, p1e = get_index_parameter(x, self.index)

        ro = numpy.zeros((3, len(x)))
        ro[:, self.index:self.index+3] = numpy.eye(3)

        return list(ro)


class FixedDirection(Constraint):
    """
    Sets a component's world coordinates so the given ``mate`` is
    orientated to the given ``world_coords``.

    There is only 1 possible solution.
    """

    def __init__(self, mate, world_coords=None):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param world_coords: world coordinates to lock ``mate`` to
        :type world_coords: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :raises TypeError: if an invalid parameter type is passed

        If the ``world_coords`` parameter is set as a
        :class:`Mate <cqparts.constraint.Mate>` instance, the mate's
        ``.world_coords`` is used.

        If ``world_coords`` is ``None``, the object is locked to the origin.
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # world_coords
        if isinstance(world_coords, CoordSystem):
            self.world_coords = world_coords
        elif isinstance(world_coords, Mate):
            self.world_coords = world_coords.world_coords
        elif world_coords is None:
            self.world_coords = CoordSystem()
        else:
            raise TypeError(
                "world_coords must be a %r or %r, not a %r" % (Mate, CoordSystem, type(world_coords))
            )

        self.l1x = numpy.array(self.mate.local_coords.xDir.toTuple())
        self.l1z = numpy.array(self.mate.local_coords.zDir.toTuple())

    def add_solver(self, solver):
        self.solver = solver
        self.index = solver.components.index(self.mate.component) * 6

        # Adding solver world_coords for compatibility reasons
        target_coords = self.world_coords + solver.world_coords

        self.xDir = numpy.array(target_coords.xDir.toTuple())
        self.zDir = numpy.array(target_coords.zDir.toTuple())

    def f(self, x):
        _, p1e = get_index_parameter(x, self.index)
        rot = get_Rot(*p1e)
        xDir = rot.dot(self.l1x)
        zDir = rot.dot(self.l1z)

        rx = xDir - self.xDir
        rz = zDir - self.zDir

        return list(rx) + list(rz)

    def df(self, x):
        _, p1e = get_index_parameter(x, self.index)

        rx = numpy.zeros((3, len(x)))
        rx[:, self.index+3] = get_Rot_dalpha(*p1e).dot(self.l1x)
        rx[:, self.index+4] = get_Rot_dbeta(*p1e).dot(self.l1x)
        rx[:, self.index+5] = get_Rot_dgamma(*p1e).dot(self.l1x)

        rz = numpy.zeros((3, len(x)))
        rz[:, self.index+3] = get_Rot_dalpha(*p1e).dot(self.l1z)
        rz[:, self.index+4] = get_Rot_dbeta(*p1e).dot(self.l1z)
        rz[:, self.index+5] = get_Rot_dgamma(*p1e).dot(self.l1z)

        return list(rx) + list(rz)

class Fixed(Constraint):
    """
    Sets a component's world coordinates so the given ``mate`` is
    positioned and orientated to the given ``world_coords``.

    There is only 1 possible solution.
    """

    def __init__(self, mate, world_coords=None):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param world_coords: world coordinates to lock ``mate`` to
        :type world_coords: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :raises TypeError: if an invalid parameter type is passed

        If the ``world_coords`` parameter is set as a
        :class:`Mate <cqparts.constraint.Mate>` instance, the mate's
        ``.world_coords`` is used.

        If ``world_coords`` is ``None``, the object is locked to the origin.
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # world_coords
        if isinstance(world_coords, CoordSystem):
            self.world_coords = world_coords
        elif isinstance(world_coords, Mate):
            self.world_coords = world_coords.world_coords
        elif world_coords is None:
            self.world_coords = CoordSystem()
        else:
            raise TypeError(
                "world_coords must be a %r or %r, not a %r" % (Mate, CoordSystem, type(world_coords))
            )

        self.position = FixedPosition(mate, world_coords)
        self.direction = FixedDirection(mate, world_coords)

    def add_solver(self, solver):
        self.position.add_solver(solver)
        self.direction.add_solver(solver)

    def f(self, x):
        return list(self.position.f(x)) + list(self.direction.f(x))

    def df(self, x):
        return list(self.position.df(x)) + list(self.direction.df(x))
