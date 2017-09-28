
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

    def _profile_to_cross_section(self, profile, min_vertices=10):
        """
        Converts a thread profile to it's equivalent cross-section.

        Profile:
            The thread profile contains a single wire along the XZ plane
            (note: wire will be projected onto the XZ plane; Y-coords wil be ignored).
            The profile is expected to be of 1 thread rotation, so it's height
            (along the Z-axis) is the thread's "lead".
            note: If there are multiple starts to a thread, then the profile
            will show the repetition.

        Method:
            Each edge of the profile is converted to a bezier spline, aproximating
            it's polar plot equivalent.

        Resolution: (via `min_vertices` parameter)
            Increasing the number of vertices used to define the bezier will
            increase the resulting thread's accuracy, but cost more to render.

            min_vertices may also be expressed as a list to set the number of
            vertices to set for each wire.
            where: len(min_vertices) == number of edges in profile

        Example:
            import cadquery
            from Helpers import show
            profile = cadquery.Workplane("XZ") \
                .moveTo(1, 0) \
                .lineTo(2, 1).lineTo(1, 2) \
                .wire()
            thread = Thread()
            cross_section = thread._profile_to_cross_section(
                profile, min_vertices=20  # increase default resolution
            )
            show(profile)
            show(cross_section)

        :param profile: cadquery.Workplane wire of thread profile
        :param min_vertices: int or tuple of the desired resolution
        :return: cadquery.Workplane ready to be swept into a thread
        """
        # verify parameter(s)
        if not isinstance(profile, cadquery.Workplane):
            raise TypeError("profile %r must be a %s instance" % (profile, cadquery.Workplane))
        if not isinstance(min_vertices, (int, list, tuple)):
            raise TypeError("min_vertices %r must be an int, list, or tuple" % (min_vertices))

        # get wire from Workplane
        wire = profile.val()  # cadquery.Wire
        if not isinstance(wire, cadquery.Wire):
            raise TypeError("a valid profile Wire type could not be found in the given Workplane")

        profile_bb = wire.BoundingBox()
        lead = profile_bb.zmax - profile_bb.zmin

        # determine vertices count per edge
        edges = wire.Edges()
        vertices_count = None
        if isinstance(min_vertices, int):
            # evenly spread vertices count along profile wire
            # (weighted by the edge's length)
            vertices_count = [
                int(ceil(round(e.Length() / wire.Length(), 7) * min_vertices))
                for e in edges
            ]
            # rounded for desired contrived results
            # (trade-off: an error of 1 is of no great consequence)
        else:
            # min_vertices is defined per edge (already what we want)
            if len(min_vertices) != len(edges):
                raise ValueError("")
            vertices_count = min_vertices

        # Utilities for building cross-section
        def get_xz(vertex):
            if isinstance(vertex, cadquery.Vector):
                vertex = vertex.wrapped  # TODO: remove this, it's messy
            # where isinstance(vertex, FreeCAD.Base.Vector)
            return (vertex.x, vertex.z)

        def cart2polar(x, z):
            """
            Convert cartesian coordinates to polar coordinates.
            Uses thread's lead height to give full 360deg translation.
            """
            radius = x
            angle = (z / lead) * (2 * pi)  # radians
            return (radius, -angle)

        def transform(vertex):
            # where isinstance(vertex, FreeCAD.Base.Vector)
            """
            Transform profile vertex on the XZ plane to it's equivalent on
            the cross-section's XY plane
            """
            (radius, angle) = cart2polar(*get_xz(vertex))
            return (radius * cos(angle), radius * sin(angle))

        # Conversion methods
        def apply_spline(wp, edge, vert_count):
            """
            Trace along edge and create a spline from the transformed verteces.
            """
            iter_dist = edge.Length() / vert_count
            points = []
            for j in range(vert_count):
                dist = (j + 1) * iter_dist
                vert = edge.wrapped.valueAt(dist)
                points.append(transform(vert))
            return wp.spline(points)

        def apply_arc(wp, edge):
            """
            Create an arc using edge's midpoint and endpoint.
            Only intended for use for vertical lines on the given profile.
            """
            return wp.threePointArc(
                point1=transform(edge.wrapped.valueAt(edge.Length() / 2)),
                point2=transform(edge.wrapped.valueAt(edge.Length())),
            )

        def apply_radial_line(wp, edge):
            """
            Create a straight radial line
            """
            return wp.lineTo(*transform(edge.endPoint()))

        # Build cross-section
        start_v = edges[0].startPoint().wrapped
        cross_section = cadquery.Workplane("XY") \
            .moveTo(*transform(start_v))

        for (i, edge) in enumerate(wire.Edges()):
            # where: isinstance(edge, cadquery.Edge)
            if (edge.geomType() == 'LINE') and (edge.startPoint().x == edge.endPoint().x):
                # edge is a vertical line, plot a circular arc
                cross_section = apply_arc(cross_section, edge)
            elif (edge.geomType() == 'LINE') and (edge.startPoint().z == edge.endPoint().z):
                # edge is a horizontal line, plot a radial line
                cross_section = apply_radial_line(cross_section, edge)
            else:
                # create bezier spline along transformed points (default)
                cross_section = apply_spline(cross_section, edge, vertices_count[i])

        return cross_section.close()
