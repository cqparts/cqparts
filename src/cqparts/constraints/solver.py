
from .base import Constraint
from .lock import LockConstraint, RelativeLockConstraint

def solver(constraints):
    """
    Solve for valid part transform matrices for the given list of mates

    :param constraints: constraints to solve
    :type constraints: list of :class:`Mate`
    """
    for constraint in constraints:
        # LockConstraint
        if isinstance(constraint, LockConstraint):
            yield (constraint.component, constraint.mate)

        # RelativeLockConstraint
        elif isinstance(constraint, RelativeLockConstraint):
            relative_coords = constraint.relative_to.world_coords
            if relative_coords:
                yield (constraint.component, relative_coords + constraint.mate)

        # Error cases
        elif not isinstance(constraint, Comstraint):
            # Element isn't a constraint
            raise ValueError("{:r} is not a constraint".format(constraint))
        else:
            # Element is a constraint, but was not caught above
            raise NotImplementedError("{:r} solving has not been implemented".format(constraint))
