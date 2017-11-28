import os
import sys
import inspect

if 'MYSCRIPT_DIR' in os.environ:
    _this_path = os.environ['MYSCRIPT_DIR']
else:
    _this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', '..', 'src'))

import cadquery
from Helpers import show

import cqparts

# Block Tree?
#
#   This is a simple concept intended to test mating parts.
#   There are 2 types of part:
#       - a cylinder
#       - a "house" shaped block (a rectangle with a triangle on top)
#           like this...
#                     /\
#                    /  \
#                   |    |
#                   |____|
#
#   Mates are positioned in the Part instances, which are used by the Assembly.
#   These building blocks are used to create a sort of wooden "tree".


# TODO: that thing what's described above.
