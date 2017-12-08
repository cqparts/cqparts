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

from cqparts.solidtypes.threads.iso_262 import ISO262Thread

import logging
log = logging.getLogger(__name__)

# Timing tools
from time import time
from contextlib import contextmanager
@contextmanager
def measure_time(name):
    start_time = time()
    yield
    taken = time() - start_time
    log.info("    %-25s (took: %gs)" % (name, taken))


with measure_time('triangular'):
    my_thread = ISO262Thread(radius=3).make(5)

# Display
show(my_thread)
