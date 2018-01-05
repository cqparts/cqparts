
from .evaluator import Evaluator

class Selector(object):
    """
    Facilitates the selection of a Fastener based on an evaluation
    """
    def __init__(self, evaluator):
        """
        :param evaluator: evaluator of fastener parts
        :type evaluator: :class:`Evaluator`
        """
        self.evaluator = evaluator

        self._components = None
        self._constraints = None

    def get_components(self):
        """
        Return components
        """
        return {}

    @property
    def components(self):
        if self._components is None:
            self._components = self.get_components()
        return self._components

    def get_constraints(self):
        return []

    @property
    def constraints(self):
        if self._constraints is None:
            self._constraints = self.get_constraints()
        return self._constraints
