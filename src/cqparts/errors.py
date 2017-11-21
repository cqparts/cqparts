

# Build Exceptions
class ParameterError(Exception):
    """Raised when an invalid parameter is specified"""

class MakeError(Exception):
    """Raised when there are issues during the make() process of a Part or Assembly"""

# Internal Search Exceptions
class AssemblyFindError(Exception):
    """Raised """


# Search Exceptions
class SearchError(Exception):
    """Raised by cqparts.find()"""

class SearchNoneFoundError(SearchError):
    """Raised when no results are found by :meth:`cqparts.search.find`"""

class SearchMultipleFoundError(SearchError):
    """Raised when multiple results are found by :meth:`cqparts.search.find`"""
