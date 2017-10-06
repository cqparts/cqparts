
class Evaluation(object):
    """
    Given a list of parts, and a linear edge, which parts will be affected?
    also use to assess:
        - first part
        - last (anchor) part
        - start & finish points on each effected part
            (the start being closer to the head)
    """
    pass


class Selector(object):
    """
    Facilitates the selection of a Fastener based on an evaluation
    """
    pass


class Applicator(object):
    """
    Effects workpieces to suit a given Fastener based on an Evaluation.
    """
    pass
