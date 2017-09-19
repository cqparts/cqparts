import cadquery
from math import pi, sin, cos

from .base import Thread

class TriangularThread(Thread):
    radius_inner = 2.5

    def get_cross_section(self, *largs, style='linear', **kwargs):
        if style == 'linear':
            return self._get_cross_section_linear(*largs, **kwargs)
        elif style == 'arcs':
            return self._get_cross_section_arcs(*largs, **kwargs)
        raise ValueError("cross-section style '%s' not supported" % style)

    def _get_cross_section_linear(self):
        points = []
        segments = 3
        for i in range(segments):
            angle = i * ((2 * pi) / segments)
            points.append((
                self.radius * cos(angle),
                self.radius * sin(angle)
            ))
        return cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close()

    def helical_path(self, pitch, length, radius, angle=0):
        wire = cadquery.Wire.makeHelix(pitch, length, radius, angle=angle)
        shape = cadquery.Wire.combine([wire])
        path = cadquery.Workplane("XY").newObject([shape])
        return path

    def make(self):
        # --- Cross Section
        cross_section = self.get_cross_section('linear')

        # --- Sweep cross-section
        path = self.helical_path(self.pitch, self.length, self.radius)
        thread = cross_section.sweep(path, isFrenet=True)

        return thread
