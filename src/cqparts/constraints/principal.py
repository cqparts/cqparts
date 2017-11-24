
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

        Individual rotation & translation matricies are:

        .. math::

            R_z & = \begin{bmatrix}
                cos(\alpha) & -sin(\alpha) & 0 & 0 \\
                sin(\alpha) & cos(\alpha) & 0 & 0 \\
                0 & 0 & 1 & 0 \\
                0 & 0 & 0 & 1
            \end{bmatrix} \qquad & R_y & = \begin{bmatrix}
                cos(\beta) & 0 & sin(\beta) & 0 \\
                0 & 1 & 0 & 0 \\
                -sin(\beta) & 0 & cos(\beta) & 0 \\
                0 & 0 & 0 & 1
            \end{bmatrix} \\
            \\
            R_x & = \begin{bmatrix}
                1 & 0 & 0 & 0 \\
                0 & cos(\gamma) & -sin(\gamma) & 0 \\
                0 & sin(\gamma) & cos(\gamma) & 0 \\
                0 & 0 & 0 & 1
            \end{bmatrix} \qquad & T_{\text{xyz}} & = \begin{bmatrix}
                1 & 0 & 0 & \delta x \\
                0 & 1 & 0 & \delta y \\
                0 & 0 & 1 & \delta z \\
                0 & 0 & 0 & 1
            \end{bmatrix}

        The ``transform`` is the combination of these:

        .. math::

            transform = T_{\text{xyz}} \cdot R_z \cdot R_y \cdot R_x = \begin{bmatrix}
                a & b & c & \delta x \\
                d & e & f & \delta y \\
                g & h & i & \delta z \\
                0 & 0 & 0 & 1
            \end{bmatrix}

        Where:

        .. math::

            a & = cos(\alpha) cos(\beta) \\
            b & = cos(\alpha) sin(\beta) sin(\gamma) - sin(\alpha) cos(\gamma) \\
            c & = cos(\alpha) sin(\beta) cos(\gamma) + sin(\alpha) sin(\gamma) \\
            d & = sin(\alpha) cos(\beta) \\
            e & = sin(\alpha) sin(\beta) sin(\gamma) + cos(\alpha) cos(\gamma) \\
            f & = sin(\alpha) sin(\beta) cos(\gamma) - cos(\alpha) sin(\gamma) \\
            g & = -sin(\beta) \\
            h & = cos(\beta) sin(\gamma) \\
            i & = cos(\beta) cos(\gamma) \\

        But generally you shouldn't have to worry about the complexities; you can
        use the tools...

        .. warning::

            TODO: what **are** these "tools"?

        """
