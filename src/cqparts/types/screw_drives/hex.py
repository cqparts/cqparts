import cadquery
from math import sqrt, pi, sin, cos

from .base import ScrewDrive, screw_drive
from ...utils.geometry import copy
from ...params import *


@screw_drive('hex', 'allen')
class HexScrewDrive(ScrewDrive):
    diameter = PositiveFloat(None)
    width = PositiveFloat(ScrewDrive.diameter.default * cos(pi / 6))  # if set, defines diameter
    count = IntRange(1, None, 1)  # number of hexagon cutouts

    # Tamper resistance pin
    pin = Boolean(False)  # if True, a pin is placed in the center
    pin_height = None  # defaults to depth
    pin_diameter = None # defaults to diameter / 3

    def initialize_parameters(self):
        super(HexScrewDrive, self).initialize_parameters()
        if self.width is not None:
            # Set diameter from hexagon's width (ignore given diameter)
            self.diameter = self.width / cos(pi / 6)

        if self.pin_height is None:
            self.pin_height = self.depth
        if self.pin_diameter is None:
            self.pin_diameter = self.diameter / 3

    def get_hexagon_vertices(self):
        """
        Generate the points of a hexagon
        :param diameter: Diameter of hexagon
        :return: list of tuples [(x1, y1), (x2, y2), ... ]
        """
        radius = self.diameter / 2.0
        points = []
        for i in range(6):
            theta = (i + 0.5) * (pi / 3)
            points.append((cos(theta) * radius, sin(theta) * radius))
        return points

    def apply(self, workplane, offset=(0, 0, 0)):
        # Single hex as template
        points = self.get_hexagon_vertices()
        tool_template = cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(-self.depth)

        # Create tool (rotate & duplicate template)
        tool = copy(tool_template)
        for i in range(1, self.count):
            angle = i * (60.0 / self.count)
            tool = tool.union(
                copy(tool_template).rotate((0, 0, 0), (0, 0, 1), angle)
            )

        # Tamper Resistance Pin
        if self.pin:
            tool = tool.faces("<Z").circle(self.pin_diameter / 2.).cutBlind(self.pin_height)

        return workplane.cut(tool.translate(offset))


@screw_drive('double_hex', '2hex')
class DoubleHexScrewDrive(HexScrewDrive):
    count = IntRange(1, None, 2)


@screw_drive('hexalobular')
class HexalobularScrewDrive(ScrewDrive):
    count = IntRange(1, None, 6)
    gap = PositiveFloat(None)  # gap beetween circles at diameter (defaults to diameter / 8)
    fillet = PositiveFloat(None)  # defaults to gap / 2

    # Tamper resistance pin
    pin = Boolean(False)  # if True, a pin is placed in the center
    pin_height = PositiveFloat(None)  # defaults to depth
    pin_diameter = PositiveFloat(None) # defaults to diameter / 3

    def initialize_parameters(self):
        super(HexalobularScrewDrive, self).initialize_parameters()
        if self.gap is None:
            self.gap = self.diameter / 8
        if self.fillet is None:
            self.fillet = self.gap / 2
        if self.pin_height is None:
            self.pin_height = self.depth
        if self.pin_diameter is None:
            self.pin_diameter = self.diameter / 3

    def apply(self, workplane, offset=(0, 0, 0)):
        # Start with a circle with self.diameter
        tool = cadquery.Workplane("XY") \
            .circle(self.diameter / 2).extrude(-self.depth)

        # Cut cylinders from circumference
        wedge_angle = (2 * pi) / self.count
        outer_radius = (self.diameter / 2.) / cos(wedge_angle / 2)
        cut_radius = (outer_radius * sin(wedge_angle / 2)) - (self.gap / 2)

        cylinder_template = cadquery.Workplane("XY") \
            .center(0, outer_radius) \
            .circle(cut_radius) \
            .extrude(-self.depth)

        for i in range(self.count):
            angle = (360. / self.count) * i
            tool = tool.cut(cylinder_template.rotate((0, 0, 0), (0, 0, 1), angle))

        # Fillet the edges before cutting
        if self.fillet:
            tool = tool.edges("|Z").fillet(self.fillet)

        # Tamper Resistance Pin
        if self.pin:
            tool.faces("<Z").circle(self.pin_diameter / 2.).cutBlind(self.pin_height)

        return workplane.cut(tool.translate(offset))
