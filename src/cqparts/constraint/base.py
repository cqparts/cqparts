

class Constraint(object):
    """
    A means to limit the relative position &/or motion of 1 or more components.

    Constraints are combined and solved to set world coordinates of the
    components within an assembly.
    """

    # def solve(self): ??????
    #   Qustion: how do grouped conditions get solved?
    #
    #   For Example:
    #       Constraints:
    #           - lock rotation
    #           - vector
    #           - vector (intersecting 1st vector constraint)
    #       All constraints reference the same Component.
    #       There's only 1 solution; at the intersection point.
    #
    #       A single constraint cannot provide a solution, they must
    #       be combined... so a self.solve() won't work unless the
    #       constraints are linked... I think that would be messy and confusing.
