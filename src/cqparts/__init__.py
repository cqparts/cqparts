# =========================== Package Information ===========================
# Version Planning:
#   0.1.x               - Development Status :: 2 - Pre-Alpha
#   0.2.x               - Development Status :: 3 - Alpha
#   0.3.x               - Development Status :: 4 - Beta
#   1.x                 - Development Status :: 5 - Production/Stable
#   <any above>.y       - developments on that version (pre-release)
#   <any above>*.dev*   - development release (intended purely to test deployment)
__version__ = "0.1.0"

__title__ = "cqparts"
__description__ = "Parts and Assemblies for cadquery"
__url__ = "https://github.com/fragmuffin/cqparts"

__author__ = "Peter Boin"
__email__ = "peter.boin@gmail.com"

__license__ = "GPLv3"

# not text-parsable
__copyright__ = "Copyright 2017 {0}".format(__author__)


# =========================== Imports ===========================
__all__ = [
    'basic',
    'bearings',
    'fasteners',
    'gears',
    'motors',
    'torque_limiters',

    'solidtypes',

    'display',
    'errors',
    'params',
    'part',
    'search',
    'utils',

    'constraint',

    # Sub-modules
    # bringing scope closer to cqparts for commonly used classes
    'Component',
    'Part',
    'Assembly',
]

from . import basic
from . import bearings
from . import fasteners
from . import gears
from . import motors
from . import torque_limiters

from . import solidtypes

from . import display
from . import errors
from . import params
from . import part
from . import search
from . import utils

from . import constraint

# Sub-modules
from .part import Component
from .part import Part
from .part import Assembly
