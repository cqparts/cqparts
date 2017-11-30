
from ..utils.geometry import CoordSystem
from .base import Constraint
from .lock import LockConstraint, RelativeLockConstraint

def solver(constraints, coord_sys=None):
    """
    Solve for valid part transform matrices for the given list of mates

    :param constraints: constraints to solve
    :type constraints: list of :class:`Mate`
    :param coord_sys: coordinate system to offset solutions
    :type coord_sys: :class:`CoordSystem`
    """

    if coord_sys is None:
        coord_sys = CoordSystem()  # default

    # Verify list contains constraints
    for constraint in constraints:
        if not isinstance(constraint, Constraint):
            # Element isn't a constraint
            raise ValueError("{:r} is not a constraint".format(constraint))

    solved_count = 0

    indexed = list(constraints)

    # Continue running solver until no solution is found
    while indexed:
        indexes_solved = []
        for (i, constraint) in enumerate(indexed):
            # LockConstraint
            if isinstance(constraint, LockConstraint):
                indexes_solved.append(i)
                yield (constraint.component, coord_sys + constraint.mate)

            # RelativeLockConstraint
            elif isinstance(constraint, RelativeLockConstraint):
                relative_coords = constraint.relative_to.world_coords
                if relative_coords:
                    indexes_solved.append(i)
                    # note: relative_coords are world coordinates, applying coord_sys is not necessary
                    yield (constraint.component, relative_coords + constraint.mate)

        if not indexes_solved:  # no solutions found
            # At least 1 solution must be found each iteration.
            # if not, we'll just be looping forever.
            break
        else:
            # remove constraints from indexed list (so they're not solved twice)
            for j in reversed(indexes_solved):
                del indexed[j]

    if indexed:
        raise ValueError("not all constraints could be solved")
