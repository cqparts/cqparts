import six
from math import ceil, sin, cos, pi

import cadquery
import FreeCAD
import Part as FreeCADPart

# relative imports
from ...params import *

import logging
log = logging.getLogger(__name__)

# Creating a thread can be done in a number of ways:
#   - cross-section helical sweep
#       - can't be tapered
#   - profile helical sweep
#       - difficult (or impossible) to do without tiny gaps, and a complex
#           internal helical structure forming the entire thread
#   - negative profile helical sweep cut from cylinder
#       - expensive, helical sweept object is only used to do an expensive cut

def profile_to_cross_section(profile, lefthand=False, start_count=1, min_vertices=20):
    """
    Converts a thread profile to it's equivalent cross-section.

    Profile:
        The thread profile contains a single wire along the XZ plane
        (note: wire will be projected onto the XZ plane; Y-coords wil be ignored).
        The profile is expected to be of 1 thread rotation, so it's height
        (along the Z-axis) is the thread's "pitch".
        If start_count > 1, then the profile will effectively be duplicated.
        The resulting cross-section is designed to be swept along a helical path
        with a pitch of the thread's "lead" (which is {the height of the given
        profile} * start_count)

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
        cross_section = profile_to_cross_section(profile)
        show(profile)
        show(cross_section)

    :param profile: cadquery.Workplane wire of thread profile
    :param lefthand: if True, cross-section is made backwards
    :param start_count: profile is duplicated this many times
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
    pitch = profile_bb.zmax - profile_bb.zmin
    lead = pitch * start_count

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
            raise ValueError(
                "min_vertices list size does not match number of profile edges: "
                "len(%r) != %i" % (min_vertices, len(edges))
            )
        vertices_count = min_vertices

    # Utilities for building cross-section
    def get_xz(vertex):
        if isinstance(vertex, cadquery.Vector):
            vertex = vertex.wrapped  # TODO: remove this, it's messy
        # where isinstance(vertex, FreeCAD.Base.Vector)
        return (vertex.x, vertex.z)

    def cart2polar(x, z, z_offset=0):
        """
        Convert cartesian coordinates to polar coordinates.
        Uses thread's lead height to give full 360deg translation.
        """
        radius = x
        angle = ((z + z_offset) / lead) * (2 * pi)  # radians
        if not lefthand:
            angle = -angle
        return (radius, angle)

    def transform(vertex, z_offset=0):
        # where isinstance(vertex, FreeCAD.Base.Vector)
        """
        Transform profile vertex on the XZ plane to it's equivalent on
        the cross-section's XY plane
        """
        (radius, angle) = cart2polar(*get_xz(vertex), z_offset=z_offset)
        return (radius * cos(angle), radius * sin(angle))

    # Conversion methods
    def apply_spline(wp, edge, vert_count, z_offset=0):
        """
        Trace along edge and create a spline from the transformed verteces.
        """
        curve = edge.wrapped.Curve  # FreeCADPart.Geom* (depending on type)
        if edge.geomType() == 'CIRCLE':
            iter_dist = edge.wrapped.ParameterRange[1] / vert_count
        else:
            iter_dist = edge.Length() / vert_count
        points = []
        for j in range(vert_count):
            dist = (j + 1) * iter_dist
            vert = curve.value(dist)
            points.append(transform(vert, z_offset))
        return wp.spline(points)

    def apply_arc(wp, edge, z_offset=0):
        """
        Create an arc using edge's midpoint and endpoint.
        Only intended for use for vertical lines on the given profile.
        """
        return wp.threePointArc(
            point1=transform(edge.wrapped.valueAt(edge.Length() / 2), z_offset),
            point2=transform(edge.wrapped.valueAt(edge.Length()), z_offset),
        )

    def apply_radial_line(wp, edge, z_offset=0):
        """
        Create a straight radial line
        """
        return wp.lineTo(*transform(edge.endPoint(), z_offset))

    # Build cross-section
    start_v = edges[0].startPoint().wrapped
    cross_section = cadquery.Workplane("XY") \
        .moveTo(*transform(start_v))

    for i in range(start_count):
        z_offset = i * pitch
        for (j, edge) in enumerate(wire.Edges()):
            # where: isinstance(edge, cadquery.Edge)
            if (edge.geomType() == 'LINE') and (edge.startPoint().x == edge.endPoint().x):
                # edge is a vertical line, plot a circular arc
                cross_section = apply_arc(cross_section, edge, z_offset)
            elif (edge.geomType() == 'LINE') and (edge.startPoint().z == edge.endPoint().z):
                # edge is a horizontal line, plot a radial line
                cross_section = apply_radial_line(cross_section, edge, z_offset)
            else:
                # create bezier spline along transformed points (default)
                cross_section = apply_spline(cross_section, edge, vertices_count[j], z_offset)

    return cross_section.close()


def helical_path(pitch, length, radius, angle=0, lefthand=False):
    # FIXME: update to master branch of cadquery
    wire = cadquery.Wire(FreeCADPart.makeHelix(pitch, length, radius, angle, lefthand))
    #wire = cadquery.Wire.makeHelix(pitch, length, radius, angle=angle, lefthand=lefthand)
    shape = cadquery.Wire.combine([wire])
    path = cadquery.Workplane("XY").newObject([shape])
    return path


class MinVerticiesParam(Parameter):
    def type(self, value):
        if isinstance(value, int):
            return max(2, value)
        elif isinstance(value, list):
            cast_value = []
            for v in value:
                if isinstance(v, int):
                    cast_value.append(self.cast(v))
                else:
                    raise ParameterError("list contains at least one value that isn't an integer: %r" % v)
            return cast_value
        else:
            raise ParameterError("min_vertices must be an integer, or a list of integers: %r" % value)


class Thread(ParametricObject):
    # Base parameters
    pitch = PositiveFloat(1.0)
    start_count = IntRange(1, None, 1)
    min_vertices = MinVerticiesParam(20)
    radius = PositiveFloat(3.0)

    inner = Boolean(False)  # if set, thread made is intended to be cut from a solid to form an inner thread
    lefthand = Boolean(False)

    def build_profile(self):
        """
        Build the thread's profile in a cadquery.Workplace as a wire
        example:
            points = [
                (2, 0), (3, 0.5), (3, 1), (2, 1.5), (2, 2)
            ]
            profile = cadquery.Workplane("XZ") \
                .moveTo(*points[0]).polyline(points[1:])
            return profile.wire()
        """
        raise NotImplementedError("build_profile function not overridden in %s" % type(self))

    def make(self, length):
        # Make cross-section
        profile = self.build_profile()
        cross_section = profile_to_cross_section(
            self.build_profile(),
            lefthand=self.lefthand,
            start_count=self.start_count,
            min_vertices=self.min_vertices,
        )

        # Make helical path
        profile_bb = profile.val().BoundingBox()
        #lead = (profile_bb.zmax - profile_bb.zmin) * self.start_count
        lead = self.pitch * self.start_count
        path = helical_path(lead, length, 1, lefthand=self.lefthand)

        # Sweep into solid
        thread = cross_section.sweep(path, isFrenet=True)

        # Making thread a valid solid
        # FIXME: this should be implemented inside cadquery itself
        thread_shape = thread.objects[0].wrapped
        if not thread_shape.isValid():
            log.warning("thread shape not valid")
            new_thread = thread_shape.copy()
            new_thread.sewShape()
            thread.objects[0].wrapped = FreeCADPart.Solid(new_thread)
            if not thread.objects[0].wrapped.isValid():
                log.error("new thread STILL not valid")

        #solid = thread.val().wrapped
        #face = App.ActiveDocument.Face.Shape.copy()


        return thread


# Thread register
#   Create your own custom thread like so...
#
#       import cadquery
#       from Helpers import show
#       from cqparts.params import *
#       from cqparts.types.threads import Thread, thread
#
#       @thread('my_thread')  # registration is not mandatory, but recommended
#       class MyThread(Thread):
#           my_param = FloatRange(0, 5, 2.5)  # for example
#
#           def build_profile(self):
#               points = [
#                   (self.my_param, 0),
#                   (self.radius, self.pitch/2),
#                   (self.my_param, self.pitch),
#               ]
#               profile = cadquery.Workplane("XZ") \
#                   .moveTo(*points[0]).polyline(points[1:])
#               return profile.wire()
#
#       t = MyThread(radius=4, my_param=3.1).make(length=5)
#       show(t)  # renders thread in FreeCAD

thread_map = {}


def thread(*names):
    assert all(isinstance(n, six.string_types) for n in names), "bad thread name"
    def inner(cls):
        """
        Add thread class to mapping
        """
        assert issubclass(cls, ScrewDrive), "class must inherit from ScrewDrive"
        for name in names:
            assert name not in thread_map, "more than one thread named '%s'" % name
            thread_map[name] = cls
        return cls

    return inner


def find(name):
    return thread_map[name]
