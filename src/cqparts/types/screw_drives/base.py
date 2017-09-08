import six
import cadquery


class ScrewDrive(object):
    diameter = 3.0
    depth = 3.0

    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

    def apply(self, workplane):
        """
        Application of screwdrive indentation into a workplane (centred around it's origin)
        """
        raise NotImplementedError("apply function not overridden in %r" % self)


screw_drive_map = {}

def screw_drive(*names):
    assert all(n for n in names isinstance(n, six.string_types)), "bad screw drive name"
    def inner(cls):
        """
        Add screw drive class to mapping
        """
        assert issubclass(cls, ScrewDrive), "class must inherit from ScrewDrive"
        for name in names:
            assert name not in screw_drive_map, "more than one screw_drive named '%s'" % name
            screw_drive_map[name] = cls
        return cls

    return inner
