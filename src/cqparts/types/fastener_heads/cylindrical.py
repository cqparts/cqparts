import cadquery
from math import pi, cos, sin, sqrt

from .base import FastenerHead, fastener_head
from cqparts.utils import intersect  # FIXME: fix is in master


class CylindricalFastenerHead(FastenerHead):
    fillet = None  # defaults to diameter / 10

    # Dome on top ?
    domed = False
    dome_ratio = 0.25  # ratio of head's height

    def make(self, offset=(0, 0, 0)):
        head = cadquery.Workplane("XY") \
            .circle(self.diameter / 2.).extrude(self.height)

        if self.domed:
            dome_height = self.height * self.dome_ratio
            sphere_radius = ((dome_height ** 2) + ((self.diameter / 2.) ** 2)) / (2 * dome_height)

            sphere = cadquery.Workplane("XY") \
                .workplane(offset=self.height - sphere_radius) \
                .sphere(sphere_radius)

            #head = head.intersect(sphere)  # FIXME: fix is in master
            head = intersect(head, sphere)

        else:
            # Fillet top face
            fillet = self.diameter / 10 if self.fillet is None else self.fillet
            if fillet:
                head = head.faces(">Z").edges().fillet(fillet)

        return head.translate(offset)


@fastener_head('cheese')
class CheeseFastenerHead(CylindricalFastenerHead):
    fillet = 0.0
    domed = False


@fastener_head('pan')
class PanFastenerHead(CylindricalFastenerHead):
    domed = False


@fastener_head('dome')
class DomeFastenerHead(CylindricalFastenerHead):
    domed = True


@fastener_head('round')
class RoundFastenerHead(CylindricalFastenerHead):
    domed = True
    dome_ratio = 1.0


@fastener_head('trapezoidal')
class TrapezoidalFastenerHead(FastenerHead):
    diameter_top = None  # default to diameter * 0.75

    def make(self, offset=(0, 0, 0)):
        diameter_top = self.diameter * 0.75 if self.diameter_top is None else self.diameter_top
        r1 = self.diameter / 2.
        r2 = diameter_top / 2.
        head = cadquery.Workplane("XY").union(
            cadquery.CQ(cadquery.Solid.makeCone(r1, r2, self.height))
        )

        return head.translate(offset)
