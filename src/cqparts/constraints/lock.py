
from .base import Constraint
from .mate import Mate


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


class RelativeLockConstraint(Constraint):
    """
    Locks an object to a coordinate system offset relative to a part.

    To successfully determine the component's location, the relative component
    must be solvable.

    .. note::
        An :class:`Assembly <cqparts.part.Assembly>` **cannot** solely rely
        on relative locks to place its components.
        This is because every component will be waiting for another component
        to be placed, a circular problem.

        At least one of them must use the :class:`LockConstraint`
    """
    def __init__(self, component, mate, relative_to):
        """
        :param component: component being constrained
        :type component: :class:`Component <cqparts.part.Component>`
        :param mate: mate to lock component's coordinate system to
        :type mate: :class:`Mate <cqparts.constraints.base.Mate>`
        :param relative_to: ``mate`` is set in this component's coordinate system
        :type relative_to: :class:`Component <cqparts.part.Component>`
        """
        self.component = component
        self.mate = mate
        self.relative_to = relative_to
