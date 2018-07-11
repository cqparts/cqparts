
.. _fasteners.easy-install.parts:


Component Parts
--------------------------

The composition of this fastener is relatively simple; we smiply have 2 parts
grouped into a single mechanical fastener.

::

    easy_fastener_1
       ├─○ wood_screw
       └─○ anchor

And to demonstrate its function, these will be used to connect 2 wooden panels.
So we'll need the panels too.

Wood Screw
^^^^^^^^^^^^^^^^^^

Wood screw will use :class:`MaleFastenerPart <cqparts_fasteners.male.MaleFastenerPart>`
as a basis.

* **screw body** : built from
  :class:`MaleFastenerPart <cqparts_fasteners.male.MaleFastenerPart>`, then modified.
* **shaft** : we'll add the bore-sized shaft (with some cylindrical cut-outs)
  to the neck of the screw.

.. doctest::

    import cadquery
    import cqparts
    from cqparts.params import *
    from cqparts_fasteners.params import HeadType, DriveType, ThreadType
    from cqparts_fasteners.male import MaleFastenerPart
    from cqparts.display import display, render_props
    from cqparts.constraint import Mate
    from cqparts.utils import CoordSystem


    class WoodScrew(MaleFastenerPart):
        # --- override MaleFastenerPart parameters
        # sub-parts
        head = HeadType(default=('cheese', {
            'diameter': 4,
            'height': 2,
        }), doc="screw's head")
        drive = DriveType(default=('phillips', {
            'diameter': 3.5,
            'depth': 2.5,
            'width': 0.5,
        }), doc="screw's drive")
        thread = ThreadType(default=('triangular', {
            'diameter': 5,  # outer
            'diameter_core': 4.3,  # inner
            'pitch': 2,
            'angle': 30,
        }), doc="screw's thread")

        # scalars
        neck_diam = PositiveFloat(2, doc="neck diameter")
        neck_length = PositiveFloat(40, doc="length from base of head to end of neck")
        length = PositiveFloat(50, doc="length from base of head to end of thread")

        # --- parameters unique for this class
        neck_exposed = PositiveFloat(2, doc="length of neck exposed below head")
        bore_diam = PositiveFloat(6, doc="diameter of screw's bore")

        _render = render_props(template='aluminium')

        def initialize_parameters(self):
            super(WoodScrew, self).initialize_parameters()

        def make(self):
            screw = super(WoodScrew, self).make()

            # add bore cylinder
            bore = cadquery.Workplane('XY', origin=(0, 0, -self.neck_length)) \
                .circle(self.bore_diam / 2) \
                .extrude(self.neck_length - self.neck_exposed)
            # cut out sides from bore so it takes less material
            for angle in [i * (360 / 3) for i in range(3)]:
                slice_obj = cadquery.Workplane(
                    'XY',
                    origin=(self.bore_diam / 2, 0, -(self.neck_exposed + 2))
                ).circle(self.bore_diam / 3) \
                    .extrude(-(self.neck_length - self.neck_exposed - 4)) \
                    .rotate((0,0,0), (0,0,1), angle)
                bore = bore.cut(slice_obj)
            screw = screw.union(bore)

            return screw

        def make_cutter(self):
            # we won't use MaleFastenerPart.make_cutter() because it
            # implements an access hole that we don't need.
            cutter = cadquery.Workplane('XY', origin=(0, 0, self.head.height)) \
                .circle(self.bore_diam / 2) \
                .extrude(-(self.neck_length + self.head.height))
            cutter = cutter.union(
                self.thread.make_pilothole_cutter().translate((
                    0, 0, -self.length
                ))
            )
            return cutter

        def make_simple(self):
            # in this case, the cutter solid serves as a good simplified
            # model of the screw.
            return self.make_cutter()

        @property
        def mate_threadstart(self):
            return Mate(self, CoordSystem(origin=(0, 0, -self.neck_length)))


So to illustrate what we've just made::

    screw = Screw()
    display(screw)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/easy-install/screw.html"
        height="300px" width="100%"
    ></iframe>


Anchor
^^^^^^^^^^^^^^

The anchor is composed of:

* **main body** : the anchor will be cut from a large cylindrical block.
* **neck slot** : slot allowing woodscrew's neck access.
* **head slot** : conical wedge to pull on screwhead when installed.
* **access port** : 1 quadrant cut out to to allow screwhead access.
* **screw drive** : to allow user to apply a screwdriver to install.

.. doctest::

    from math import sin, cos, pi

    class Anchor(cqparts.Part):
        # sub-parts
        drive = DriveType(default=('cross', {
            'diameter': 5,
            'width': 1,
            'depth': 2.5,
        }), doc="anchor's drive")

        # scalars
        diameter = PositiveFloat(10, doc="diameter of anchor")
        height = PositiveFloat(5, doc="height of anchor")
        neck_diameter = PositiveFloat(2, doc="width of screw neck")
        head_diameter = PositiveFloat(4, doc="width of screw head")
        spline_point_count = IntRange(4, 200, 10, doc="number of spiral spline points")
        ratio_start = FloatRange(0.5, 0.99, 0.99, doc="radius ratio of wedge start")
        ratio_end = FloatRange(0.01, 0.8, 0.7, doc="radius ratio of wedge end")

        _render = render_props(color=(100, 100, 150))  # dark blue

        @property
        def wedge_radii(self):
            return (
                (self.diameter / 2) * self.ratio_start,  # start radius
                (self.diameter / 2) * self.ratio_end  # end radius
            )

        def make(self):
            obj = cadquery.Workplane('XY') \
                .circle(self.diameter / 2) \
                .extrude(-self.height)

            # neck slot : eliminate screw neck interference
            obj = obj.cut(
                cadquery.Workplane('XY', origin=(0, 0, -((self.neck_diameter + self.height) / 2))) \
                    .moveTo(0, 0) \
                    .lineTo(self.diameter / 2, 0) \
                    .threePointArc(
                        (0, -self.diameter / 2),
                        (-self.diameter / 2, 0),
                    ) \
                    .close() \
                    .extrude(self.neck_diameter)
            )

            # head slot : form a circular wedge with remaining material
            (start_r, end_r) = self.wedge_radii
            angles_radius = (  # as generator
                (
                    (i * (pi / self.spline_point_count)),  # angle
                    start_r + ((end_r - start_r) * (i / float(self.spline_point_count)))  # radius
                )
                for i in range(1, self.spline_point_count + 1)  # avoid zero angle
            )
            points = [(cos(a) * r, -sin(a) * r) for (a, r) in angles_radius]
            obj = obj.cut(
                cadquery.Workplane('XY', origin=(0, 0, -((self.head_diameter + self.height) / 2))) \
                    .moveTo(start_r, 0) \
                    .spline(points) \
                    .close() \
                    .extrude(self.head_diameter)
            )

            # access port : remove a quadrant to allow screw's head through
            obj = obj.cut(
                cadquery.Workplane('XY', origin=(0, 0, -(self.height - self.head_diameter) / 2)) \
                    .rect(self.diameter / 2, self.diameter / 2, centered=False) \
                    .extrude(-self.height)
            )

            # screw drive : to apply torque to anchor for installation
            if self.drive:
                obj = self.drive.apply(obj)  # top face is on origin XY plane

            return obj

        def make_simple(self):
            # Just return the core cylinder
            return cadquery.Workplane('XY') \
                .circle(self.diameter / 2) \
                .extrude(-self.height)

        def make_cutter(self):
            # A solid to cut away from another; makes room to install the anchor
            return cadquery.Workplane('XY', origin=(0, 0, -self.height)) \
                .circle(self.diameter / 2) \
                .extrude(self.height + 1000)  # 1m bore depth

        @property
        def mate_screwhead(self):
            # The location of the screwhead in it's theoretical tightened mid-point
            #   (well, not really, but this is just a demo)
            (start_r, end_r) = self.wedge_radii
            return Mate(self, CoordSystem(
                origin=(0, -((start_r + end_r) / 2), -self.height / 2),
                xDir=(1, 0, 0),
                normal=(0, 1, 0)
            ))

        @property
        def mate_center(self):
            # center of object, along screw's rotation axis
            return Mate(self, CoordSystem(origin=(0, 0, -self.height / 2)))

        @property
        def mate_base(self):
            # base of object (for 3d printing placement, maybe)
            return Mate(self, CoordSystem(origin=(0, 0, -self.height)))


What we've made isn't perfect, but it will do for this tutorial.
Besides, that's more than enough code::

    anchor = Anchor()
    display(anchor)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/easy-install/anchor.html"
        height="300px" width="100%"
    ></iframe>


Wood Panel
^^^^^^^^^^^^^

We'll also need to create some wooden panels that we intend to join using
the *fastener*.

It's essentially just a *box* shape, but we'll add some *mate* points to allow
easy alignment.

.. doctest::

    class WoodPanel(cqparts.Part):
        thickness = PositiveFloat(15, doc="thickness of panel")
        width = PositiveFloat(100, doc="panel width")
        length = PositiveFloat(100, doc="panel length")

        def make(self):
            return cadquery.Workplane('XY') \
                .box(self.length, self.width, self.thickness)

        @property
        def mate_end(self):
            # center of +x face
            return Mate(self, CoordSystem(
                origin=(self.length / 2, 0, 0),
                xDir=(0, 0, -1),
                normal=(-1, 0, 0),
            ))

        def get_mate_edge(self, thickness):
            return Mate(self, CoordSystem(
                origin=((self.length / 2) - (thickness / 2), 0, self.thickness / 2)
            ))

::

    panel = WoodPanel()
    display(panel)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/easy-install/panel.html"
        height="300px" width="100%"
    ></iframe>


Now that we have all the parts we need, the next section will work on combining
these into an *assembly*.
