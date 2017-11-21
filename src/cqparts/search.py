from collections import defaultdict
from copy import copy

# Search Index
#   of the format:
#       index = {
#           <category>: {
#               <value>: set([<set of classes>]),
#               ... more values
#           },
#           ... more categories
#       }
index = defaultdict(lambda: defaultdict(set))
class_list = set()
class_criteria = {}


def register(**criteria):
    """
    class decorator to add :class:`Part` or :class:`Assembly` to qcparts

    usage::

        import cqparts

        # Created Part or Assembly
        @cqparts.search.register(
            type='motor',
            current_class='dc',
            part_number='ABC123X',
        )
        class SomeMotor(cqparts.Assembly):
            def make(self):
                return {}  # build assembly content

        motor_class = cqparts.search.find(part_number='ABC123X')
        motor = motor_class(shaft_diameter=6.0)

    .. warning::

        Multiple classes *can* be registered with identical criteria, but
        should be avoided.

        If multiple classes share the same criteria, :meth:`find` will never
        yield the part you want.

        Try adding unique criteria, such as *make*, *model*, *part number*,
        *library name*, &/or *author*.
    """

    def inner(cls):
        # Add class references to search index
        class_list.add(cls)
        for (category, value) in criteria.items():
            index[category][value].add(cls)

        # Retain search criteria
        class_criteria[cls] = criteria

        # Return class
        return cls

    return inner


def search(**criteria):
    """
    Search registered part classes matching the given criteria.

    :param criteria: search criteria of the form: ``a='1', b='x'``
    :return: parts registered with the given criteria
    :rtype: :class:`set`

    Will return an empty :class:`set` if nothing is found.

    ::

        from cqparts.search import search
        import cqparts_motors  # example of a 3rd party lib

        # Get all DC motor classes
        dc_motors = search(type='motor', current_class='dc')

        # For more complex queries:
        air_cooled = search(cooling='air')
        non_aircooled_dcmotors = dc_motors - air_cooled
        # will be all DC motors that aren't air-cooled
    """
    # Find all parts that match the given criteria
    results = copy(class_list)  # start with full list
    for (category, value) in criteria.items():
        results &= index[category][value]

    return results


def find(**criteria):
    """
    Find a single part class with the given criteria:

    :raises SearchMultipleFoundError: if more than one result found
    :raises SearchNoneFoundError: if nothing found

    ::

        from cqparts.search import find
        import cqparts_motors  # example of a 3rd party lib

        # get a specific motor class
        motor_class = find(type='motor', part_number='ABC123X')
        motor = motor_class(shaft_diameter=6.0)
    """
    # Find all parts that match the given criteria
    results = search(**criteria)

    # error cases
    if len(results) > 1:
        raise SearchMultipleFoundError("%i results found" % len(results))
    elif not results:
        raise SearchNoneFoundError("%i results found" % len(results))

    # return found Part|Assembly class
    return results.pop()
