
from .base import Constraint


class LockConstraint(Constraint):
    """
    Locks an object to a coordinate system offset.

    There is only 1 possible solution.

    Essentially
    """

    def __init__(self, transform):
        r"""
        Explicitly locks a part's coordinate system.

        :param transform: 4x4 array of coordinate system lock
        :type transform: :class:`numpy.ndarray`

        .. math::

           transform = \begin{bmatrix}
              a & b & c & x \\
              d & e & f & y \\
              g & h & i & z \\
              0 & 0 & 0 & 1
           \end{bmatrix}
        """
