from .evaluator import VectorEvaluator, CylinderEvaluator

class Applicator(object):
    """
    Effects workpieces to suit a given Fastener based on an Evaluator.
    """

    compatible_eval_classes = (VectorEvaluator, CylinderEvaluator)

    #def __init__(self, evaluator):
    #    self.evaluator =
