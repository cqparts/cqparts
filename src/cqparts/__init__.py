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
__copyright__ = "Copyright 2018 {0}".format(__author__)


# =========================== Imports ===========================
__all__ = [
    # Sub-modules
    # bringing scope closer to cqparts for commonly used classes
    'Component',
    'Part',
    'Assembly',

    # Modules
    'codec',
    'constraint',
    'display',
    'errors',
    'params',
    'search',
    'utils',
]

# Sub-modules
from .component import Component
from .part import Part
from .assembly import Assembly

from . import codec
from . import constraint
from . import display
from . import errors
from . import params
from . import search
from . import utils
