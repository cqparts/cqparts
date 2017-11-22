from .evaluator import VectorEvaluator, CylinderEvaluator

class Applicator(object):
    """
    The *applicator* performs 2 roles to *apply* a fastener to workpieces

    #. Translate & rotate given *fastener*
    #. Change workpieces to suit a given *fastener*

    Translation is done first because the fastener is sometimes used as a
    cutting tool to subtract from mating part(s) (eg: thread tapping).
    """

    compatible_eval_classes = (VectorEvaluator, CylinderEvaluator)

    #def __init__(self, evaluator):
    #    self.evaluator =
