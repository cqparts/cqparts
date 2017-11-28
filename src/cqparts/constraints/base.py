

class Constraint(object):
    """
    A means to limit the relative position &/or motion of 1 or more components.

    Constraints are combined and solved to set world coordinates of the
    components within an assembly.
    """

    def conditions_met(self):
        """
        :return: True if a solution may be attempted
        :rtype: :class:`bool`

        .. note::

            The ``Constraint`` class is a base class for all constriants.

            It should never be used on its own. See :ref:`parts.constraints`
            for details
        """
        raise NotImplementedError("conditions_met not implemented for %r" % type(self))

    # def solve(self): ??????
