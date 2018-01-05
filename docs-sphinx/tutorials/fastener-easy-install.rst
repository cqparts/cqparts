
.. _tutorials_fastener-easy-install:

Fastener : Easy Install
=======================

This example illustrates how to make the classic *build-it-yourself*
furniature fastener for wood panels connected at right angels.

.. figure:: img/easy-install-manual-eg.png

    Example of the instructions you may find in a manual.

Component Parts
---------------

The composition of this fastener is relatively simple; we smiply have 2 parts
grouped into a single mechanical fastener.

::

    easy_fastener_1
       ├─○ wood_screw
       └─○ anchor

Wood Screw
^^^^^^^^^^

Wood screw will use :class:`MaleFastenerPart <cqparts_fasteners.male.MaleFastenerPart>`
as a basis.

* **screw body** : built from
  :class:`MaleFastenerPart <cqparts_fasteners.male.MaleFastenerPart>`, then modified.
* **shaft** : we'll add the bore-sized shaft to the neck of the screw.

::

    import cadquery
    import cqparts
    from cqparts.params import *
    from cqparts_fasteners.params import HeadType, DriveType, ThreadType
    from cqparts_fasteners.male import MaleFastenerPart
    from cqparts.display import display

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
            cutter = cadquery.Workplane('XY') \
                .circle(self.bore_diam / 2) \
                .extrude(-self.neck_length)
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


So to illustrate what we've just made::

    screw = Screw()
    display(screw)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/easy-install/screw.html"
        height="300px" width="100%"
    ></iframe>


Anchor
^^^^^^

The anchor is composed of:

* **main body** : the anchor will be cut from a large cylindrical block.
* **neck slot** : slot alowing woodscrew's neck access.
* **head slot** : conical wedge to pull on screwhead when installed.
* **access port** : 1 quadrant cut out to to alow screwhead access.
* **screw drive** : to allow user to apply a screwdriver to install.

::

    from math import sin, cos, pi
    from cqparts.utils import CoordSystem
    from cqparts.constraint import Mate

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

        @property
        def conical_radii(self):
            return (
                (self.diameter / 2) * self.ratio_start,  # start radius
                (self.diameter / 2) * self.ratio_end  # end radius
            )

        def make(self):
            obj = cadquery.Workplane('XY') \
                .circle(self.diameter / 2) \
                .extrude(-self.height)

            # neck slot
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

            # head slot (forms a conical wedge)
            (start_r, end_r) = self.conical_radii
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

            # access port
            obj = obj.cut(
                cadquery.Workplane('XY', origin=(0, 0, -(self.height - self.head_diameter) / 2)) \
                    .rect(self.diameter / 2, self.diameter / 2, centered=False) \
                    .extrude(-self.height)
            )

            # screw drive
            if self.drive:
                obj = self.drive.apply(obj)

            return obj

        def make_simple(self):
            return cadquery.Workplane('XY') \
                .circle(self.diameter / 2) \
                .extrude(-self.height)

        @property
        def mate_screwhead(self):
            (start_r, end_r) = self.conical_radii
            return Mate(self, CoordSystem(
                origin=(0, -((start_r + end_r) / 2), -self.height / 2),
                xDir=(1, 0, 0),
                normal=(0, 1, 0)
            ))


What we've made isn't perfect, but it will do for this tutorial.
Besides, that's more than enough code::

    anchor = Anchor()
    display(anchor)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/easy-install/anchor.html"
        height="300px" width="100%"
    ></iframe>


Aligned Together
^^^^^^^^^^^^^^^^^^^^^

Just to demonstrate what we've made, let's create a temporary
:class:`Assembly <cqparts.Assembly>` aligning the 2 together:

.. doctest::

    from cqparts.constraint import Fixed, Coincident

    class _Together(cqparts.Assembly):
        def make_components(self):
            return {
                'screw': WoodScrew(neck_exposed=5),
                'anchor': Anchor(height=7),
            }

        def make_constraints(self):
            return [
                Fixed(self.components['screw'].mate_origin),
                Coincident(
                    self.components['anchor'].mate_screwhead,
                    self.components['screw'].mate_origin,
                ),
            ]

::

    together = _Together()
    display(together)

.. raw:: html

    <iframe class="model-display"
        src="../_static/iframes/easy-install/together.html"
        height="300px" width="100%"
    ></iframe>


Evaluation / Selection / Application
------------------------------------

.. currentmodule:: cqparts_fasteners.utils

Now we need to assess the logic behind the application of this
fastening mechanism.

.. tip::

    *Evaluation*, *selection*, and *application* are fundamental concepts for
    using fasteners as more than just floating objects, read
    :ref:`parts_fasteners_using` to learn more.

To do this manually, we'd have to:

* **evaluate** (or measure) the diameter and depth of the woodscrew's pilot hole, as well
  as the location and size of the anchor's cylindrical bore on the vertical workpiece.
* **select** an apropriately sized wood-screw and anchor (based on the
  evaluation we've made).
* **apply** the pilot hole, and anchor's bore. Then screw in the wood-screw,
  insert the anchor, and then put it all together.


Evaluator
^^^^^^^^^

We can use the :class:`VectorEvaluator` to do most of the work for us.

If we give the :class:`VectorEvaluator` a vector through the middle of the
vertical part, with a starting point at, or above, the anchor's desired location,
then it will give us the maximum length of the screw (not including it's thread),
and the available depth for the wood-screw's thread.

However, what this *doesn't* give us is the orientation of the *anchor*.
So we also need to give the evaluator a face through which the anchor's bore will
be applied::


    from cqparts_fasteners.utils.evaluator import VectorEvaluator
    class EasyInstallEvaluator(VectorEvaluator):
        def __init__(self, parts, start, dir, anchor_plane):
            super(EasyInstallEvaluator, self).__init__(parts, start, dir)
            self.anchor_plane = anchor_plane

        @property
        def anchor_norm(self):
            return self.anchor_plane.zDir

.. todo::

    image of evaluation, showing:

    * input vector
    * output effect vectors


Selection
^^^^^^^^^

To illustrate the selection mechanic, we'll register 2 types of *wood screw*
for this fastener:

#. 20mm shaft, 10mm thread
#. 40mm shaft, 15mm thread

and 2 types of *anchor*:

#. 15mm diameter
#. 20mm diameter

The selector will choose a *wood screw* with the longest shaft, with a thread
that taps into <= 80% of the adjoining piece.

::

    from cqparts_fasteners.utils.selector import Selector

    class EasyInstallSelector(Selector):
        #TODO: code for selector
        # note: selector must return a wood-screw and anchor
        #       does it return a Fastener instance?
        pass

        def get_selection(self):
            # TODO: returns single Fastener instance
            # if there are multiple viable choices, it's up to the selector
            # to narrow it down to a single selection.
            pass

Application
^^^^^^^^^^^

The evaluation should result in 2
:class:`VectorEffect <evaluator.VectorEffect>` instances, one for
each part.

::

    from cqparts_fasteners.utils.applicator import Applicator

    class EasyInstallApplicator(Applicator):
        # TODO: code for applicator
        pass


Fastener Assembly
-----------------

So now we have the 2 components, we can combine these into a
:class:`Fastener <cqparts_fasteners.base.Fastener>`.

::

    from cqparts_fasteners import Fastener

    class EasyInstallFastener(Fastener):
        EVALUATOR_CLASS = EasyInstallEvaluator
        SELECTOR_CLASS = EasyInstallSelector
        APPLICATOR_CLASS = EasyInstallApplicator

        def make(self):
            screw = WoodScrew()  # TODO: parameters + mate

            anchor = Anchor()  # TODO: parameters + mate

            return {
                'wood_screw': screw,
                'anchor': anchor,
            }


Using the Fastener
------------------

Now that we've made it, this is how it can be imported and used.

First let's make some parts to join together::

    # fixme: pretending it's there
    import cadquery
    import cqparts

    class Panel1(cqparts.Part):
        def make(self):
            return cadquery.Workplane('XY', origin=(0, -50, -10)) \
                .box(100, 100, 10, centered=(False, False, False))

    class Panel2(cqparts.Part):
        def make(self):
            return cadquery.Workplane('XY', origin=(0, -50, 0)) \
                .box(10, 100, 100, centered=(False, False, False))

Now we import and use the ``EasyinstallFastener`` we've created::

    from cqparts_mylib.easyinstall import EasyInstallFastener

    # TODO: 2 instances of the same panel, different orientation
    panel1 = Panel1()
    panel2 = Panel2()

    evaluation = EasyInstallFastener.evaluate(
        parts
