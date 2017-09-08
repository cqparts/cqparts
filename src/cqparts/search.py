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

def register_class(cls):
    """
    class decorator to add class to qcparts
    usage:
        import cqparts
        @cqparts.register_class
        class SomeMotor(cqparts.Assembly):
            INDEX_CRITERIA = {
                'type': 'motor',
                'class': 'dc',
                'part_number': 'ABC123X',
            }
            def make(self):
                return {}  # build assembly content

        motor_class = cqparts.find(part_number='ABC123X')
        motor = motor_class(shaft_diameter=6.0)
        
    note: nothing is stopping 2 parts from having identical index criteria.
    however, this means it will be impossible to isolate it using cqparts.find.
    you should either use cqparts.search (which will return both classes), or
    preferably more INDEX_CRITERIA added to uniquely identify the differences
    between parts.
    """
    # Add class references to search index
    class_list.add(cls)
    for (category, value) in cls.INDEX_CRITERIA.items():
        index[category][value].add(cls)

    # Return unaltered class
    return cls


def search(**kwargs):
    """
    Search registered parts matching the given criteria
    :return: set of
    """
    # Find all parts that match the given criteria
    results = copy(class_list)  # start with full list
    for (category, value) in kwargs.items():
        results &= index[category][value]

    return results


def find(**kwargs):
    """
    Find part with the given criteria
    """
    # Find all parts that match the given criteria
    results = search(**kwargs)

    # error cases
    if len(results) > 1:
        raise SearchMultipleFoundError("%i results found" % len(results))
    elif not results:
        raise SearchNoneFoundError("%i results found" % len(results))

    # return found Part|Assembly class
    return results.pop()
