
Component Parts
--------------------------

Wood Panel
^^^^^^^^^^^^^^^^^^

.. doctest::

    from math import radians, tan, cos
    import cadquery

    import cqparts
    from cqparts.params import *
    from cqparts.constraint import Mate
    from cqparts.utils import CoordSystem

    from cqparts.display import display, render_props


    class Panel(cqparts.Part):
        # dimensions
        height = PositiveFloat(50, doc="panel height (along join)")
        depth = PositiveFloat(50, doc="panel depth (from join to opposite side)")
        width = PositiveFloat(10, doc="thickness of panel")

        # join
        join_angle = FloatRange(0, 89, 45, doc="angle of join (unit: degrees)")

        _render = render_props(template='wood', alpha=0.5)

        def make(self):
            points = [
                (0, 0),
                (self.depth, 0),
                (self.depth, self.width),
                (self.width * tan(radians(self.join_angle)), self.width),
            ]
            return cadquery.Workplane('XZ', origin=(0, self.height / 2, 0)) \
                .moveTo(*points[0]).polyline(points[1:]).close() \
                .extrude(self.height)

        @property
        def mate_join(self):
            return self.get_mate_join(ratio=0.5)

        @property
        def mate_join_reverse(self):
            return self.mate_join + CoordSystem().rotated((180, 0, 0))

        def get_mate_join(self, ratio=0.5):
            # Return a mate that's somewhere along the join surface.
            return Mate(self, (
                CoordSystem().rotated(
                    (0, -(90 - self.join_angle), 0)
                ) + CoordSystem(
                    origin=(
                        (self.width / cos(radians(self.join_angle))) / 2,
                        (-self.height / 2) + (self.height * ratio),
                        0
                    ),
                )
            ))

So to illustrate what we've just made::

    panel = Panel()
    display(panel)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/biscuit/panel.html"
        height="300px" width="100%"
    ></iframe>


Biscuit
^^^^^^^^^^^^^

.. doctest::

    class Biscuit(cqparts.Part):
        # Biscuit Dimensions
        width = PositiveFloat(30, doc="twice penetration depth")
        length = PositiveFloat(None, doc="length tip to tip")
        thickness = PositiveFloat(5, doc="material thickness")

        _render = render_props(template='wood_dark')

        def initialize_parameters(self):
            super(Biscuit, self).initialize_parameters()
            if self.length is None:
                self.length = (5. / 3) * self.width

        def make(self):
            # We'll just use the simplified model for this example
            return self.make_simple()
            # It could be rounded at the ends, and the sides chamfered, but
            # for this example we'll just keep it simple.

        def make_simple(self):
            biscuit = cadquery.Workplane('XY')

            # Create left & right side, union them together
            for i in [1, -1]:
                biscuit = biscuit.union(
                    cadquery.Workplane('XY', origin=(0, 0, -self.thickness / 2)) \
                        .moveTo(self.length / 2, 0) \
                        .threePointArc(
                            (0, i * self.width / 2),
                            (-self.length / 2, 0)
                        ).close().extrude(self.thickness)
                )

            return biscuit

        def make_cutter(self):
            return self.make_simple()

So to illustrate what we've just made::

    biscuit = Biscuit()
    display(biscuit)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/biscuit/biscuit.html"
        height="300px" width="100%"
    ></iframe>
