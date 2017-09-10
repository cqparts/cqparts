import os
import sys
import inspect

if 'MYSCRIPT_DIR' in os.environ:
    _this_path = os.environ['MYSCRIPT_DIR']
else:
    _this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'src'))

import cadquery
import math
from Helpers import show
import cqparts
from cqparts.types.screw_drives.base import screw_drive_map
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

# Screw Types
gap = 2
box_size = 5
box_height = 5

index_width = int(math.sqrt(len(set(screw_drive_map.values()))))
types_displayed = set()

with measure_time('TOTAL'):

    i = 0
    for screw_type in sorted(screw_drive_map.keys()):

        screw_drive_class = screw_drive_map[screw_type]
        if screw_drive_class in types_displayed:
            continue
        types_displayed.add(screw_drive_class)


        try:
            box = cadquery.Workplane("XY").rect(box_size, box_size).extrude(-box_height)

            row = (i % index_width)
            col = int(i / index_width)
            with measure_time("[c%i, r%i]: %s" % (col + 1, row + 1, screw_type)):
                box = screw_drive_class().apply(box)

            # Display result
            show(box.translate((
                row * (box_size + gap),
                -col * (box_size + gap),
                0
            )), (204, 204, 204, 0.5))

        except Exception as e:
            fc_print("    %-25s (%s)\n" % (screw_type, str(e)))
            #raise  # comment this out to continue rendering

        i += 1
