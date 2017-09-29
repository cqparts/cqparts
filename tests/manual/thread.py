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

from cqparts.types.threads.ball_screw import BallScrewThread
from cqparts.utils import fc_print

# Timing tools
from time import time
from contextlib import contextmanager
@contextmanager
def measure_time(name):
    start_time = time()
    yield
    taken = time() - start_time
    fc_print("    %-25s (took: %gs)\n" % (name, taken))


with measure_time('triangular'):
    my_thread = BallScrewThread().make()

# Display
show(my_thread)
