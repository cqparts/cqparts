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

    # Coach Head
    coach_head = False
    coach_width = None  # default = diameter / 2
    coach_height = None  # default = height
    coach_chamfer = None  # default = coach_width / 6

    def make(self, offset=(0, 0, 0)):
        head = super(RoundFastenerHead, self).make(offset=offset)

        # Add chamfered square block beneath fastener head
        if self.coach_head:
            coach_width = self.diameter / 2. if self.coach_width is None else self.coach_width
            coach_height = self.height if self.coach_height is None else self.coach_height
            coach_chamfer = coach_width / 6. if self.coach_chamfer is None else self.coach_chamfer
            cone_radius = ((coach_width / 2.) + coach_height) - coach_chamfer
            cone_height = cone_radius

            box = cadquery.Workplane("XY").rect(coach_width, coach_width).extrude(-coach_height)
            cone = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(0, cone_radius, cone_height)) \
                    .translate((0, 0, -cone_height))
            )
            head = head.union(intersect(box, cone))

        return head


@fastener_head('round_coach')
class RoundCoachFastenerHead(RoundFastenerHead):
    coach_head = True


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
