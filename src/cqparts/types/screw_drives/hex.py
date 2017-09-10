import cadquery
from math import sqrt, pi, sin, cos
from .base import ScrewDrive, screw_drive
from cqparts.utils import copy


@screw_drive('hex', 'allen')
class HexScrewDrive(ScrewDrive):
    diameter = None
    width = ScrewDrive.diameter * cos(pi / 6)
    count = 1

    # Tamper resistance pin
    pin = False  # if True, a pin is placed in the center
    pin_height = None  # defaults to depth
    pin_diameter = None # defaults to diameter / 3

    def get_diameter(self):
        if self.diameter is None:
            return self.width / cos(pi / 6)
        return self.diameter

    def get_hexagon_vertices(self, diameter):
        """
        Generate the points of a hexagon
        :param diameter: Diameter of hexagon
        :return: list of tuples [(x1, y1), (x2, y2), ... ]
        """
        radius = diameter / 2.0
        points = []
        for i in range(6):
            theta = (i + 0.5) * (pi / 3)
            points.append((cos(theta) * radius, sin(theta) * radius))
        return points

    def apply(self, workplane, offset=(0, 0, 0)):
        diameter = self.get_diameter()

        # Single hex as template
        points = self.get_hexagon_vertices(diameter)
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
            pin_height = self.depth if self.pin_height is None else self.pin_height
            pin_diameter = diameter / 3 if self.pin_diameter is None else self.pin_diameter
            tool.faces("<Z").circle(pin_diameter / 2.).cutBlind(pin_height)

        return workplane.cut(tool.translate(offset))


@screw_drive('double_hex', '2hex')
class DoubleHexScrewDrive(HexScrewDrive):
    count = 2


@screw_drive('hexalobular')
class HexalobularScrewDrive(ScrewDrive):
    count = 6
    gap = None  # gap beetween circles at diameter (defaults to diameter / 8)
    fillet = None  # defaults to gap / 2

    # Tamper resistance pin
    pin = False  # if True, a pin is placed in the center
    pin_height = None  # defaults to depth
    pin_diameter = None # defaults to diameter / 3

    def apply(self, workplane, offset=(0, 0, 0)):
        # Start with a circle with self.diameter
        tool = cadquery.Workplane("XY") \
            .circle(self.diameter / 2).extrude(-self.depth)

        # Cut cylinders from circumference
        gap = self.gap
        if gap is None:
            gap = self.diameter / 8
        wedge_angle = (2 * pi) / self.count
        outer_radius = (self.diameter / 2.) / cos(wedge_angle / 2)
        cut_radius = (outer_radius * sin(wedge_angle / 2)) - (gap / 2)

        cylinder_template = cadquery.Workplane("XY") \
            .center(0, outer_radius) \
            .circle(cut_radius) \
            .extrude(-self.depth)

        for i in range(self.count):
            angle = (360. / self.count) * i
            tool = tool.cut(cylinder_template.rotate((0, 0, 0), (0, 0, 1), angle))

        # Fillet the edges before cutting
        fillet = self.fillet
        if fillet is None:
            fillet = gap / 2
        if fillet:
            tool = tool.edges("|Z").fillet(fillet)

        # Tamper Resistance Pin
        if self.pin:
            pin_height = self.depth if self.pin_height is None else self.pin_height
            pin_diameter = self.diameter / 3 if self.pin_diameter is None else self.pin_diameter
            tool.faces("<Z").circle(pin_diameter / 2.).cutBlind(pin_height)

        return workplane.cut(tool.translate(offset))
