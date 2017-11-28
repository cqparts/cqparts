import cadquery


def intersect(wp1, wp2, combine=True, clean=True):
    """
    Return geometric intersection between 2 cadquery.Workplane instances by
    exploiting.
    A n B = (A u B) - ((A - B) u (B - A))
    """
    solidRef = wp1.findSolid(searchStack=True, searchParents=True)

    if solidRef is None:
        raise ValueError("Cannot find solid to intersect with")
    solidToIntersect = None

    if isinstance(wp2, cadquery.CQ):
        solidToIntersect = wp2.val()
    elif isinstance(wp2, cadquery.Solid):
        solidToIntersect = wp2
    else:
        raise ValueError("Cannot intersect type '{}'".format(type(wp2)))

    newS = solidRef.intersect(solidToIntersect)

    if clean:
        newS = newS.clean()

    if combine:
        solidRef.wrapped = newS.wrapped

    return wp1.newObject([newS])

    #cp = lambda wp: wp.translate((0, 0, 0))
    #neg1 = cp(wp1).cut(wp2)
    #neg2 = cp(wp2).cut(wp1)
    #neg = neg1.union(neg2)
    #return cp(wp1).union(wp2).cut(neg)


def copy(wp):
    return wp.translate((0, 0, 0))


class CoordSystem(cadquery.Plane):
    """
    Defines the location, and rotation of an orthogonal 3 dimensional coordinate
    system.
    """

    @property
    def world_to_local_transform(self):
        r"""
        :return: 3d affine transform matrix to convert world coordinates to local coorinates.
        :rtype: :class:`cadquery.Matrix`

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
        return self.rG

    @property
    def local_to_world_transform(self):
        """
        3d affine transform to convert local coordinates to world.

        (see :meth:`Mate.world_to_local_transform` for details)
        """
        return self.fG

    def __add__(self, other):
        """
        :return: ``other`` transformed by this coordinate system
        :rtype: that of ``other``
        """
        raise NotImplementedError("I'm getting to that")
        if isinstance(other, CoordSystem):
            pass # TODO
