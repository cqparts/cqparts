import cadquery
from math import pi, sin, cos, tan, sqrt

from .base import Thread


class ISO262Thread(Thread):
    undercut_ratio = 0.5

    def build_profile(self):
        """
        Build a thread profile in specified by ISO 262
        """
        # height of sawtooth profile (along x axis)
        # (to be trunkated to make a trapezoidal thread)
        height = self.pitch * cos(pi/6)  # ISO 262
        r_maj = self.radius
        r_min = r_maj - ((5./8) * height)

        profile = cadquery.Workplane("XZ").moveTo(r_min, 0)

        # --- rising edge
        profile = profile.lineTo(r_maj, (5./16) * self.pitch)

        # --- peak
        if self.inner:
            # undercut radius (to fit flush with thread)
            # (effective radius will be altered by undercut_ratio)
            cut_radius = (self.pitch / 16) / cos(pi/6)
            # circle's center relative to r_maj
            cut_center_under_r_maj = (self.pitch / 16) * tan(pi/6)
            undercut_depth = self.undercut_ratio * (cut_radius - cut_center_under_r_maj)
            profile = profile.threePointArc(
                (r_maj + undercut_depth, (6./16) * self.pitch),
                (r_maj, (7./16) * self.pitch)
            )
        else:
            profile = profile.lineTo(r_maj, (7./16) * self.pitch)

        # --- falling edge
        profile = profile.lineTo(r_min, (12./16) * self.pitch)

        # --- valley
        if self.inner:
            profile = profile.lineTo(r_min, self.pitch)
        else:
            # undercut radius (to fit flush with thread)
            # (effective radius will be altered by undercut_ratio)
            cut_radius = (self.pitch / 8) / cos(pi/6)
            # circle's center relative to r_maj
            cut_center_under_r_maj = (self.pitch / 8) * tan(pi/6)
            undercut_depth = self.undercut_ratio * (cut_radius - cut_center_under_r_maj)
            profile = profile.threePointArc(
                (r_min - undercut_depth, (14./16) * self.pitch),
                (r_min, self.pitch)
            )

        return profile.wire()
