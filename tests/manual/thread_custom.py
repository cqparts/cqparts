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
import Part as FreeCADPart
from Helpers import show

from cqparts.types.threads.base import Thread, profile_to_cross_section, helical_path

cadquery.freecad_impl.console_logging.enable()
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


    # FIXME: this method of creating a "custom thread" is out-dated.
    #        should inherit from Thread and implement build_profile
    profile = cadquery.Workplane("XZ") \
        .moveTo(2, 0) \
        .polyline([(3, 1), (3, 1.5)]) \
        .threePointArc((2.4, 1.5), (2, 2)) \
        .lineTo(2, 2.5) \
        .threePointArc((2.5, 3), (2, 3.5)) \
        .lineTo(2, 4) \
        .wire()
    cross_section = profile_to_cross_section(
        profile, min_vertices=100  # increase default resolution
    )

    # make helix
    path = helical_path(4.0, 4.0, 1)
    thread = cross_section.sweep(path, isFrenet=True)

    # Making thread valid
    thread_shape = thread.objects[0].wrapped
    thread_shape.sewShape()
    thread.objects[0].wrapped = FreeCADPart.Solid(thread_shape)

    # cut through
    box = cadquery.Workplane("XZ", origin=(0, 2, 2)) \
        .box(8, 6, 4)
    #thread = thread.cut(box)
    #box = box.cut(thread)

show(profile)
show(cross_section)
show(thread, (200, 200, 200, 0.2))
show(box, (255, 200, 200, 0.7))

# Display
#show(my_thread)
