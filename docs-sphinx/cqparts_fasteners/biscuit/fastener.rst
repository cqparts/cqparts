
Biscuit Fastener
--------------------------

Bi-Directional Vector Evaluator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. doctest::

    from cqparts_fasteners.utils.evaluator import Evaluator, VectorEvaluator
    from cqparts_fasteners.utils.selector import Selector
    from cqparts_fasteners.utils.applicator import Applicator

    class BiDirectionalVectorEvaluator(Evaluator):
        def __init__(self, parts, location, parent=None):
            super(BiDirectionalVectorEvaluator, self).__init__(parts=parts, parent=parent)
            self.location = location
            self.eval_pos = VectorEvaluator(parts, location.rotated((180, 0, 0)))
            self.eval_neg = VectorEvaluator(parts, location)

        def perform_evaluation(self):
            return (self.eval_pos.eval, self.eval_neg.eval)


Biscuit Fastener
^^^^^^^^^^^^^^^^^^^^^^^

.. doctest::

    from cqparts.constraint import Fixed
    from cqparts_fasteners.fasteners.base import Fastener
    from itertools import chain


    class BiscuitFastener(Fastener):
        ratio = FloatRange(0, 1, 0.5, doc="ratio penetration of biscuit into parts")
        max_length = PositiveFloat(50, doc="maximum biscuit length")
        max_thickness = PositiveFloat(5, doc="maximum biscuit thickness")

        cut_biscuit_holes = Boolean(True, doc="if True, biscuit holes are cut into pannels")

        Evaluator = BiDirectionalVectorEvaluator

        class Selector(Selector):
            def get_components(self):
                # Determine maximum biscuit width from the evaluation
                (pos, neg) = self.evaluator.eval
                pos_length = abs(pos[-1].end_point - pos[0].start_point)
                neg_length = abs(neg[-1].end_point - neg[0].start_point)
                max_width = 2 * min(
                    pos_length * self.parent.ratio,
                    neg_length * self.parent.ratio
                )
                return {
                    'biscuit': Biscuit(
                        width=max_width,
                        thickness=max_width * 0.1,
                    ),
                }

            def get_constraints(self):
                #(pos, neg) = self.evaluator.eval
                return [
                    Fixed(
                        self.components['biscuit'].mate_origin,
                        CoordSystem().rotated((90, 0, 90))
                    ),
                ]

        class Applicator(Applicator):
            def apply_alterations(self):
                if not self.parent.cut_biscuit_holes:
                    return  # fastener configured to place biscuit overlapping panel

                biscuit = self.selector.components['biscuit']
                biscuit_cutter = biscuit.make_cutter()  # cutter in local coords

                effected_parts = set([
                    effect.part for effect in chain(*self.evaluator.eval[:])
                ])

                for part in effected_parts:
                    biscuit_coordsys = biscuit.world_coords - part.world_coords
                    part.local_obj = part.local_obj.cut(biscuit_coordsys + biscuit_cutter)


Corner Assembly
^^^^^^^^^^^^^^^^^^^^^^^^^

.. doctest::

    from cqparts.constraint import Fixed, Coincident


    class CornerAssembly(cqparts.Assembly):
        biscuit_count = PositiveInt(2, doc="number of biscuits")
        join_angle = FloatRange(0, 89, 45, doc="angle of join (unit: degrees)")
        biscuit_holes = Boolean(True, doc="if True, holes are cut into pannels to house biscuits")

        def make_components(self):
            components = {
                'a': Panel(join_angle=self.join_angle),
                'b': Panel(join_angle=self.join_angle),
            }
            for i in range(self.biscuit_count):
                components['f_%i' % i] = BiscuitFastener(
                    parts=[components['a'], components['b']],
                    cut_biscuit_holes=self.biscuit_holes,
                )
            return components

        def make_constraints(self):
            # position joined panels
            a = self.components['a']
            b = self.components['b']
            yield [
                Fixed(a.mate_origin),
                Coincident(
                    b.mate_join_reverse,
                    a.mate_join
                ),
            ]

            # position biscuits along join
            biscuits = [
                c for c in self.components.values()
                if isinstance(c, BiscuitFastener)
            ]
            yield [
                Coincident(
                    c.mate_origin,
                    a.get_mate_join(
                        ratio=(i + 1) * (1. / (len(biscuits) + 1))
                    )
                )
                for (i, c) in enumerate(biscuits)
            ]


So to illustrate what we've just made::

    corner_assembly = CornerAssembly()
    display(corner_assembly)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/biscuit/corner_assembly.html"
        height="300px" width="100%"
    ></iframe>

.. figure:: img/applied-45deg.png

    FreeCAD's render may be more clear (literally).

**Variations**

::

    display(CornerAssembly(join_angle=30))
    # biscuits will have more volume through parts to grip, so they'll be larger

.. image:: img/applied-30deg.png

::

    display(CornerAssembly(join_angle=60))
    # biscuits have less volume to use, so they'll be smaller

.. image:: img/applied-60deg.png
