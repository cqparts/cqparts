import cadquery
from math import pi, cos, sin, sqrt

from .base import FastenerHead, fastener_head
from cqparts.utils import intersect  # FIXME: fix is in master


class DrivenFastenerHead(FastenerHead):
    chamfer = None  # default to diameter / 10
    edges = 4
    width = None  # defaults based on number of edges, and diameter

    # Washer (optional)
    washer = False
    washer_height = None  # default to height / 6
    washer_diameter = None  # default to diameter * 1.2

    def get_cross_section_points(self):
        points = []
        d_angle = pi / self.edges
        radius = self.diameter / 2.
        for i in range(self.edges):
            angle = d_angle + ((2 * d_angle) * i)
            points.append((
                sin(angle) * radius,
                cos(angle) * radius
            ))
        return points

    def make(self, offset=(0, 0, 0)):
        points = self.get_cross_section_points()
        head = cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.height)

        chamfer = self.diameter / 10. if self.chamfer is None else self.chamfer
        if chamfer:
            cone_height = ((self.diameter / 2.) - chamfer) + self.height
            cone_radius = (self.diameter / 2.) + (self.height - chamfer)
            cone = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(cone_radius, 0, cone_height))
            )
            #head = head.intersect(cone)  # FIXME: fix is in master
            head = intersect(head, cone)

        # Washer
        if self.washer:
            washer_height = self.height / 6. if self.washer_height is None else self.washer_height
            washer_diameter = self.diameter * 1.2 if self.washer_diameter is None else self.washer_diameter
            washer = cadquery.Workplane("XY").circle(washer_diameter / 2).extrude(washer_height)
            head = head.union(washer)

        return head.translate(offset)


@fastener_head('square')
class SquareFastenerHead(DrivenFastenerHead):
    edges = 4


@fastener_head('hex')
class HexFastenerHead(DrivenFastenerHead):
    edges = 6


@fastener_head('hex_flange')
class HexFlangeFastenerHead(DrivenFastenerHead):
    edges = 6
    washer = True
