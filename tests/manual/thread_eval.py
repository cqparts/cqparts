import os
import sys
import inspect

if 'MYSCRIPT_DIR' in os.environ:
    _this_path = os.environ['MYSCRIPT_DIR']
else:
    _this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'src'))

import cadquery
import cqparts
from Helpers import show

cadquery.freecad_impl.console_logging.enable()
import logging
log = logging.getLogger(__name__)

# Make cantilever parts
class Anchor(cqparts.Part):
    def make(self):
        return cadquery.Workplane('XY', origin=(0, 0, -10)) \
            .box(10, 30, 10, centered=(True, True, False))

class Cantilever(cqparts.Part):
    def make(self):
        return cadquery.Workplane('XY', origin=(0, 20, 0)) \
            .box(10, 50, 2, centered=(True, True, False))

class Thing(cqparts.Part):
    def make(self):
        return cadquery.Workplane('XZ', origin=(0, 0, 4)) \
            .box(3, 3, 3) \
            .faces('<Y').hole(2)

anchor = Anchor()
cantilever = Cantilever()
thing = Thing()

def make_line(start, direction):
    """Single linear edge in a Wire, as an indicator"""
    start_v = cadquery.Vector(*start)
    finish_v = start_v.add(cadquery.Vector(*direction))
    edge = cadquery.Edge.makeLine(start_v, finish_v)
    wire = cadquery.Wire.assembleEdges([edge])
    return cadquery.Workplane('XY').newObject([wire])

(s1, d1) = ((0, 0, 20), (0, 0, -10))
(s2, d2) = ((0, 10, 5), d1)

# Display stuff
show(anchor.object, (204, 204, 204, 0.3))
show(cantilever.object, (204, 204, 204, 0.3))
show(thing.object, (204, 204, 204, 0.3))
show(make_line(s1, d1))
#show(make_line(s2, d2))


# ----- Fastener Evaluation
from cqparts_fasteners.utils import VectorEvaluator

evaluator = VectorEvaluator([thing, anchor, cantilever], s1, d1)
for e in evaluator.eval:
    show(e._wire_wp)
    #show(e.result)
