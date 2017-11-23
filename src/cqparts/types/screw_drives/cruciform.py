import cadquery
from cadquery import BoxSelector
from math import pi, cos, sqrt

from .base import ScrewDrive, screw_drive
from ...utils.geometry import intersect  # FIXME: fix is in master
from ...params import *


@screw_drive('frearson')
class FrearsonScrewDrive(ScrewDrive):
    width = PositiveFloat(0.5)

    def apply(self, workplane, offset=(0, 0, 0)):
        points = [
            (self.diameter / 2., 0),
            (self.width / 2., -self.depth),
            (-self.width / 2., -self.depth),
            (-self.diameter / 2., 0),
        ]
        tool_cross_x = cadquery.Workplane("XZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)
        tool_cross_y = cadquery.Workplane("YZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        tool = tool_cross_x.union(tool_cross_y)
        return workplane.cut(tool.translate(offset))


@screw_drive('phillips')
class PhillipsScrewDrive(ScrewDrive):
    width = PositiveFloat(0.5, doc="blade width")
    chamfer = PositiveFloat(None, "chamfer at top of cross section")  # defaults to width

    def initialize_parameters(self):
        super(PhillipsScrewDrive, self).initialize_parameters()
        if self.chamfer is None:
            self.chamfer = self.width

    def apply(self, workplane, offset=(0, 0, 0)):
        # Frearson style cross from center
        points = [
            (self.diameter / 2., 0),
            (self.width / 2., -self.depth),
            (-self.width / 2., -self.depth),
            (-self.diameter / 2., 0),
        ]
        tool_cross_x = cadquery.Workplane("XZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)
        tool_cross_y = cadquery.Workplane("YZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        # Trapezoidal pyramid 45deg rotated cutout of center
        # alternative: lofting 2 squares, but that was taking ~7 times longer to process
        tz_top = (sqrt(2) * self.width) + ((self.chamfer / sqrt(2)) * 2)
        tz_base = self.width / sqrt(2)  # to fit inside square at base
        points = [
            (tz_top / 2., 0),
            (tz_base / 2., -self.depth),
            (-tz_base / 2., -self.depth),
            (-tz_top / 2., 0),
        ]
        tool_tzpy1 = cadquery.Workplane("XZ").workplane(offset=-tz_top / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(tz_top)
        tool_tzpy2 = cadquery.Workplane("YZ").workplane(offset=-tz_top / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(tz_top)
        #tool_tzpy = tool_tzpy1.intersect(tool_tzpy2) \  # FIXME: fix is in master
        #    .rotate((0, 0, 0), (0, 0, 1), 45)
        tool_tzpy = intersect(tool_tzpy1, tool_tzpy2) \
            .rotate((0, 0, 0), (0, 0, 1), 45)

        tool = cadquery.Workplane("XY") \
            .union(tool_cross_x) \
            .union(tool_cross_y) \
            .union(tool_tzpy)
        return workplane.cut(tool.translate(offset))


@screw_drive('french_recess')
class FrenchRecessScrewDrive(ScrewDrive):
    width = PositiveFloat(0.5, doc="blade width")
    step_depth = PositiveFloat(None, doc="depth the step diameter takes effect")  # default to depth / 2
    step_diameter = PositiveFloat(None, doc="diameter at depth")  # default to 2/3 diameter

    def initialize_parameters(self):
        super(FrenchRecessScrewDrive, self).initialize_parameters()
        if self.step_depth is None:
            self.step_depth = self.depth / 2
        if self.step_diameter is None:
            self.step_diameter = self.diameter * (2./3)

    def apply(self, workplane, offset=(0, 0, 0)):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.step_depth) \
            .faces(">Z") \
            .rect(self.diameter, self.width).extrude(-self.step_depth) \
            .faces("<Z") \
            .rect(self.width, self.step_diameter).extrude(-(self.depth - self.step_depth)) \
            .faces("<Z") \
            .rect(self.step_diameter, self.width).extrude(self.depth - self.step_depth)
        return workplane.cut(tool.translate(offset))


@screw_drive('mortorq')
class MortorqScrewDrive(ScrewDrive):
    width = PositiveFloat(1.0)
    count = PositiveInt(4)
    fillet = PositiveFloat(0.3)

    def apply(self, workplane, offset=(0, 0, 0)):
        points = [
            (self.width / 2, self.width / 2),
            (self.width / 2, -self.width / 2),
            (-self.diameter / 2, -self.width / 2),
            (-self.diameter / 2, self.width / 2),
        ]
        rect = cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(-self.depth)
        cylinder = cadquery.Workplane("XY") \
            .center(self.width - (self.diameter / 2.), self.width / 2.) \
            .circle(self.width).extrude(-self.depth)

        #blade = rect.intersect(cylinder)  # FIXME: fix is in master
        blade = intersect(rect, cylinder)

        tool = cadquery.Workplane("XY").rect(self.width, self.width).extrude(-self.depth)
        for i in range(self.count):
            angle = i * (360. / self.count)
            tool = tool.union(blade.rotate((0, 0, 0), (0, 0, 1), angle))

        if self.fillet:
            tool = tool.edges("|Z").fillet(self.fillet)

        return workplane.cut(tool.translate(offset))


@screw_drive('pozidriv')
class PozidrivScrewDrive(ScrewDrive):
    width = PositiveFloat(0.5)
    inset_cut = PositiveFloat(None)  # defaults to width / 2

    # cross-shaped marking to indicate "Posidriv" screw drive
    markings = Boolean(True)  # if false, marking is not shown
    marking_width = PositiveFloat(0.1)
    marking_depth = PositiveFloat(0.1)

    def initialize_parameters(self):
        super(PozidrivScrewDrive, self).initialize_parameters()
        if self.inset_cut is None:
            self.inset_cut = self.width / 2

    def apply(self, workplane, offset=(0, 0, 0)):
        # Frearson style cross from center
        points = [
            (self.diameter / 2., 0),
            (self.width / 2., -self.depth),
            (-self.width / 2., -self.depth),
            (-self.diameter / 2., 0),
        ]
        tool_cross_x = cadquery.Workplane("XZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)
        tool_cross_y = cadquery.Workplane("YZ").workplane(offset=-self.width / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        # Trapezoidal pyramid inset
        # alternative: lofting 2 squares, but that was taking ~7 times longer to process
        tz_top = self.width + (2 * self.inset_cut)
        tz_base = self.width
        points = [
            (tz_top / 2., 0),
            (tz_base / 2., -self.depth),
            (-tz_base / 2., -self.depth),
            (-tz_top / 2., 0),
        ]
        tool_tzpy1 = cadquery.Workplane("XZ").workplane(offset=-tz_top / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(tz_top)
        tool_tzpy2 = cadquery.Workplane("YZ").workplane(offset=-tz_top / 2.) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(tz_top)
        #tool_tzpy = tool_tzpy1.intersect(tool_tzpy2)  # FIXME: fix is in master
        tool_tzpy = intersect(tool_tzpy1, tool_tzpy2)

        tool = cadquery.Workplane("XY") \
            .union(tool_cross_x) \
            .union(tool_cross_y) \
            .union(tool_tzpy)

        # Cross-shaped marking
        if self.markings:
            markings = cadquery.Workplane("XY") \
                .rect(self.diameter, self.marking_width).extrude(-self.marking_depth) \
                .faces(">Z") \
                .rect(self.marking_width, self.diameter).extrude(-self.marking_depth) \
                .rotate((0, 0, 0), (0, 0, 1), 45)
            tool = tool.union(markings)

        return workplane.cut(tool.translate(offset))
