
from cqparts.search import (
    register as _register,
    search as _search,
    find as _find,
)
from cqparts.search import common_criteria

module_criteria = {
    'module': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
