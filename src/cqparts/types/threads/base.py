

# Creating a thread can be done in a number of ways:
#   - cross-section helical sweep
#       - can't be tapered
#       - making a cross-section can be difficult
#   - profile helical sweep
#       - difficult (or impossible) to do without tiny gaps, and a complex
#           internal helical structure forming the entire thread
#   - negative profile helical sweep cut from cylinder
#       - expensive, helical sweept object is only used to do an expensive cut

class Thread(object):
    # Base parameters
    length = 10.0
    pitch = 1.0
    start_count = 1
    radius = 3.0

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            if not hasattr(self, key):
                raise ValueError("screw drive class {cls} does not accept a '{key}' parameter".format(
                    cls=repr(type(self)), key=key
                ))

            # Default value given to class
            default_value = getattr(self, key)

            # Cast value to the same type as the class default
            #   (mainly designed to turn ints to floats, or visa versa)
            if default_value is None:
                cast_value = value
            else:
                cast_value = type(default_value)(value)

            # Set given value
            setattr(self, key, cast_value)

    def make(self):
        """
        Creation of thread (crated at world origin)
        """
        raise NotImplementedError("make function not overridden in %r" % self)
