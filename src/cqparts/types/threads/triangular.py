import cadquery
from math import pi, sin, cos, ceil

from .base import Thread

class TriangularThread(Thread):
    radius_inner = 2.5

    def get_cross_section(self, style='linear'):
        if style == 'linear':
            return self._get_cross_section_linear()
        if style == 'spline':
            return self._get_crsos_section_splines()
        #elif style == 'true':
        #    return self._get_cross_section_true()
        raise ValueError("cross-section style '%s' not supported" % style)

    def _get_cross_section_linear(self):
        points = []
        angle_per_thread = (2 * pi) / self.start_count

        for i in range(self.start_count):
            angle = i * angle_per_thread
            points += self.spiral_points(
                start_angle=angle,
                start_radius=self.radius,
                end_angle=angle + (angle_per_thread / 2),
                end_radius=self.radius_inner,
            )
            points += self.spiral_points(
                start_angle=angle + (angle_per_thread / 2),
                start_radius=self.radius_inner,
                end_angle=angle + angle_per_thread,
                end_radius=self.radius,
            )

        return cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close()

    def _get_crsos_section_splines(self):
        angle_per_thread = (2 * pi) / self.start_count

        cross_section = cadquery.Workplane("XY").moveTo(self.radius, 0)
        for i in range(self.start_count):
            angle = i * angle_per_thread
            cross_section = cross_section.spline(self.spiral_points(
                start_angle=angle,
                start_radius=self.radius,
                end_angle=angle + (angle_per_thread / 2),
                end_radius=self.radius_inner,
                endpoint=True,
            )[1:])
            cross_section = cross_section.spline(self.spiral_points(
                start_angle=angle + (angle_per_thread / 2),
                start_radius=self.radius_inner,
                end_angle=angle + angle_per_thread,
                end_radius=self.radius,
                endpoint=True,
            )[1:])

        return cross_section.close()

    def make(self):
        # --- Cross Section
        cross_section = self.get_cross_section('spline')

        # --- Sweep cross-section
        path = self.helical_path(self.pitch, self.length, self.radius)
        thread = cross_section.sweep(path, isFrenet=True)

        return thread
