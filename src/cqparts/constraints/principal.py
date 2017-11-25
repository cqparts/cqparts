
from .base import Constraint


class LockConstraint(Constraint):
    """
    Locks an object to a coordinate system offset.

    There is only 1 possible solution.
    """

    def __init__(self, component, mate):
        """
        :param component: component being constrained
        :type component: :class:`Component <cqparts.part.Component>`
        :param mate: mate to lock component's coordinate system to
        :type mate: :class:`Mate <cqparts.constraints.base.Mate>`
        """
        self.component = component
        self.mate = mate
