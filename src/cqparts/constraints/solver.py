
from .base import Constraint
from .principal import LockConstraint

def solver(constraints):
    """
    Solve for valid part transform matrices for the given list of mates

    :param constraints: constraints to solve
    :type constraints: list of :class:`Mate`
    """
    for constraint in constraints:
        if isinstance(constraint, LockConstraint):
            yield (constraint.component, constraint.mate)

        # Error cases
        elif not isinstance(constraint, Comstraint):
            # Element isn't a constraint
            raise ValueError("{:r} is not a constraint".format(constraint))
        else:
            # Element is a constraint, but was not caught above
            raise NotImplementedError("{:r} solving has not been implemented".format(constraint))
