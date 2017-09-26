
from math import ceil, sin, cos, pi

import cadquery
import FreeCAD
import Part as FreeCADPart

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

    # ---- Common tools for threads
    def helical_path(self, pitch, length, radius, angle=0):
        wire = cadquery.Wire.makeHelix(pitch, length, radius, angle=angle)
        shape = cadquery.Wire.combine([wire])
        path = cadquery.Workplane("XY").newObject([shape])
        return path

    def spiral_points(self, start_angle, start_radius, end_angle, end_radius,
                      max_angle_step=(pi/8), endpoint=False):
        """
        Plot out a series of coordinates along a spiral (on a 2d plane)
        :return: list of tuples: [(x1, y1), (x2, y2), ... ]
        """
        # FIXME: this isn't good... needs to be a true spiral
        #        better yet; convert a profile to it's polar plot
        # Spiral range (angle & radius)
        angle_diff = end_angle - start_angle
        radius_diff = end_radius - start_radius

        # Iterate through points
        points = []
        steps = int(ceil(angle_diff / max_angle_step))
        range_steps = (steps + 1) if endpoint else steps
        for i in range(range_steps):
            angle = start_angle + (i * (angle_diff / steps))
            radius = start_radius + (i * (radius_diff / steps))
            points.append((radius * cos(angle), radius * sin(angle)))
        return points
