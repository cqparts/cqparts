import cadquery
from math import pi, cos, sin, sqrt

from .base import FastenerHead, fastener_head
from cqparts.utils import intersect  # FIXME: fix is in master

from ...params import *

class CylindricalFastenerHead(FastenerHead):
    fillet = PositiveFloat(None)  # defaults to diameter / 10

    # Dome on top ?
    domed = Boolean(False)
    dome_ratio = PositiveFloat(0.25)  # ratio of head's height

    def initialize_parameters(self):
        super(CylindricalFastenerHead, self).initialize_parameters()
        if self.fillet is None:
            self.fillet = self.diameter / 10

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
            if self.fillet:
                head = head.faces(">Z").edges().fillet(self.fillet)

        return head.translate(offset)


@fastener_head('cheese')
class CheeseFastenerHead(CylindricalFastenerHead):
    fillet = PositiveFloat(0.0)
    domed = Boolean(False)


@fastener_head('pan')
class PanFastenerHead(CylindricalFastenerHead):
    domed = Boolean(False)


@fastener_head('dome')
class DomeFastenerHead(CylindricalFastenerHead):
    domed = Boolean(True)


@fastener_head('round')
class RoundFastenerHead(CylindricalFastenerHead):
    domed = Boolean(True)
    dome_ratio = PositiveFloat(1)

    # Coach Head
    coach_head = Boolean(False)
    coach_width = PositiveFloat(None)  # default = diameter / 2
    coach_height = PositiveFloat(None)  # default = height
    coach_chamfer = PositiveFloat(None)  # default = coach_width / 6

    def initialize_parameters(self):
        super(RoundFastenerHead, self).initialize_parameters()
        if self.coach_width is None:
            self.coach_width = self.diameter / 2
        if self.coach_height is None:
            self.coach_height = self.height
        if self.coach_chamfer is None:
            self.coach_chamfer = self.coach_width / 6

    def make(self, offset=(0, 0, 0)):
        head = super(RoundFastenerHead, self).make(offset=offset)

        # Add chamfered square block beneath fastener head
        if self.coach_head:
            cone_radius = ((self.coach_width / 2.) + self.coach_height) - self.coach_chamfer
            cone_height = cone_radius

            box = cadquery.Workplane("XY").rect(self.coach_width, self.coach_width).extrude(-self.coach_height)
            cone = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(0, cone_radius, cone_height)) \
                    .translate((0, 0, -cone_height))
            )
            head = head.union(intersect(box, cone))

        return head


@fastener_head('round_coach')
class RoundCoachFastenerHead(RoundFastenerHead):
    coach_head = Boolean(True)


@fastener_head('trapezoidal')
class TrapezoidalFastenerHead(FastenerHead):
    diameter_top = PositiveFloat(None)  # default to diameter * 0.75

    def initialize_parameters(self):
        super(TrapezoidalFastenerHead, self).initialize_parameters()
        if self.diameter_top is None:
            self.diameter_top = self.diameter * 0.75

    def make(self, offset=(0, 0, 0)):
        r1 = self.diameter / 2.
        r2 = self.diameter_top / 2.
        head = cadquery.Workplane("XY").union(
            cadquery.CQ(cadquery.Solid.makeCone(r1, r2, self.height))
        )

        return head.translate(offset)
