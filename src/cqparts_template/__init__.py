
__release_ready__ = False  # TODO: remove to stop blocking build

__title__ = "cqparts_<lib_name>"  # TODO
__description__ = "<brief description>"  # TODO
__url__ = "<library url>"  # TODO

__version__ = "0.1.0"
__author__ = "<your name>"  # TODO


# ------ Registration
from cqparts.search import (
    find as _find,
    search as _search,
    register as _register,
)
from cqparts.search import common_criteria

module_criteria = {
    'library': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
