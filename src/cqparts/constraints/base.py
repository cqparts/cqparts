


# angle, coincident, concentric, distance, lock, parallel, perpendicular, and tangent mates
# limit, linear/linear coupler, path, symmetry, and width
# cam-follower, gear, hinge, rack and pinion, screw, and universal joint
#
#
# Fastened
# Revolute
# Slider
# Planar
# Cylindrical
# Pin Slot
# Ball


class Constraint(object):
    """
    A means to limit the relative position &/or motion of 2 components.


    Constraints are combined and solved to set absolute positions of the
    components within an assembly.

    .. doctest::

        >>> from cqparts.mates import Constraint
        >>> constraint = Constraint()
    """
