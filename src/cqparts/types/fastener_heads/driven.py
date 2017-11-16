import cadquery
from math import pi, cos, sin, sqrt

from .base import FastenerHead, fastener_head
from ...utils import intersect  # FIXME: fix is in master
from ...params import *


class DrivenFastenerHead(FastenerHead):
    chamfer = PositiveFloat(None)  # default to diameter / 10
    edges = PositiveInt(4)
    width = PositiveFloat(None)  # defaults based on number of edges, and diameter

    # Washer (optional)
    washer = Boolean(False)
    washer_height = PositiveFloat(None)  # default to height / 6
    washer_diameter = PositiveFloat(None)  # default to diameter * 1.2

    def initialize_parameters(self):
        super(DrivenFastenerHead, self).initialize_parameters()
        if self.width is not None:
            # Set diameter based on witdh (ignore given diameter)
            # (width is the size of the wrench used to drive it)
            self.diameter = self.width / cos(pi / self.edges)
        if self.chamfer is None:
            self.chamfer = self.diameter / 10
        if self.washer_height is None:
            self.washer_height = self.height / 6
        if self.washer_diameter is None:
            self.washer_diameter = self.diameter * 1.2

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

        if self.chamfer:
            cone_height = ((self.diameter / 2.) - self.chamfer) + self.height
            cone_radius = (self.diameter / 2.) + (self.height - self.chamfer)
            cone = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(cone_radius, 0, cone_height))
            )
            #head = head.intersect(cone)  # FIXME: fix is in master
            head = intersect(head, cone)

        # Washer
        if self.washer:
            washer = cadquery.Workplane("XY") \
                .circle(self.washer_diameter / 2) \
                .extrude(self.washer_height)
            head = head.union(washer)

        return head.translate(offset)


@fastener_head('square')
class SquareFastenerHead(DrivenFastenerHead):
    edges = PositiveInt(4)


@fastener_head('hex')
class HexFastenerHead(DrivenFastenerHead):
    edges = PositiveInt(6)


@fastener_head('hex_flange')
class HexFlangeFastenerHead(DrivenFastenerHead):
    edges = PositiveInt(6)
    washer = Boolean(True)
