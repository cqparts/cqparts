
from ..part import Part

def as_part(func):
    """
    Converts a function to an Part instance

    So the conventional code::

        import cadquery
        from cqparts import Part
        from cqparts.params import Float
        class Box(Part):
            x = Float(1)
            y = Float(2)
            z = Float(4)
            def make(self):
                return cadquery.Workplane('XY').box(self.x, self.y, self.z)
        box = Box(x=6, y=3, z=1)

    May also be written as::

        import cadquery
        from cqparts.utils.wrappers import as_part

        @as_part
        def make_box(x=1, y=2, z=4):
            return cadquery.Workplane('XY').box(x, y, z)

        box = make_box(6, 3, 1)

    """
    def inner(*args, **kwargs):
        part_class = type(func.__name__, (Part,), {
            'make': lambda self: func(*args, **kwargs),
        })
        return part_class()
    return inner
