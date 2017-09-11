import cadquery
from math import pi, cos, sin, sqrt

from .base import FastenerHead, fastener_head
from cqparts.utils import intersect  # FIXME: fix is in master

# pull FreeCAD module from cadquery (workaround for torus)
FreeCAD = cadquery.freecad_impl.FreeCAD


@fastener_head('countersunk')
class CounterSunkFastenerHead(FastenerHead):
    chamfer = None  # default to diameter / 20
    raised = 0.0  # if None, defaults to diameter / 10
    bugle = False
    bugle_ratio = 0.5 # radians, must be < pi / 4 (45 deg)

    def get_raised(self):
        if self.raised is None:
            return self.diameter / 10.
        return self.raised

    def make(self, offset=(0, 0, 0)):
        chamfer = self.diameter / 20 if self.chamfer is None else self.chamfer
        cone_radius = self.diameter / 2
        cone_height = cone_radius  # to achieve a 45deg angle
        cylinder_radius = cone_radius - chamfer
        cylinder_height = self.height
        shaft_radius = (self.diameter / 2.) - self.height

        cone = cadquery.Workplane("XY").union(
            cadquery.CQ(cadquery.Solid.makeCone(0, cone_radius, cone_height)) \
                .translate((0, 0, -cone_height))
        )

        cylinder = cadquery.Workplane("XY") \
            .circle(cylinder_radius).extrude(-cylinder_height)

        #head = cone.intersect(cylinder)  # FIXME: fix is in master
        head = intersect(cone, cylinder)

        # Raised bubble (if given)
        raised = self.get_raised()
        if raised:
            sphere_radius = ((raised ** 2) + (cylinder_radius ** 2)) / (2 * raised)

            sphere = cadquery.Workplane("XY").workplane(offset=-(sphere_radius - raised)) \
                .sphere(sphere_radius)
            raised_cylinder = cadquery.Workplane("XY").circle(cylinder_radius).extrude(raised)
            from Helpers import show

            #raised_bubble = sphere.intersect(raised_cylinder)  # FIXME: fix is in master
            raised_bubble = intersect(sphere, raised_cylinder)
            head = head.union(raised_bubble)

        # Bugle Head
        if self.bugle and (0 <= self.bugle_ratio < 1.0):
            # bugle_angle = angle head material makes with chamfer cylinder on top
            bugle_angle = (pi / 4) * self.bugle_ratio
            # face_span = longest straight distance along flat conical face (excluding chamfer)
            face_span = sqrt(2) * (((self.diameter / 2.) - chamfer) - shaft_radius)
            r2 = (face_span / 2.) / sin((pi / 4) - bugle_angle)
            d_height = r2 * sin(bugle_angle)
            r1 = (r2 * cos(bugle_angle)) + shaft_radius

            torus = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeTorus(
                    r1, r2, # radii
                    pnt=FreeCAD.Base.Vector(0,0,0),
                    dir=FreeCAD.Base.Vector(0,0,1),
                    angleDegrees1=0.,
                    angleDegrees2=360.
                )).translate((0, 0, -(self.height + d_height)))
            )
            head = head.cut(torus)

        return head.translate(offset)

    def get_face_offset(self):
        return (0, 0, self.get_raised())


@fastener_head('countersunk_raised')
class CounterSunkRaisedFastenerHead(CounterSunkFastenerHead):
    raised = None  # defaults to diameter / 10


@fastener_head('countersunk_bugle')
class CounterSunkBugleFastenerHead(CounterSunkFastenerHead):
    bugle = True
