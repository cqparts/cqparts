
.. _cqparts_fastener-built-in_screw:

.. currentmodule:: cqparts_fasteners.fasteners.screw

Screw
---------

The :class:`ScrewFastener` fastener penetrates through all the given parts
with a countersunk phillips head screw.

The last part's hole is a pilot hole.

.. doctest::

    import cqparts
    from cqparts.constraint import Fixed, Coincident
    from cqparts_fasteners.fasteners.screw import ScrewFastener
    from cqparts_misc.basic.primatives import Box

    class Thing(cqparts.Assembly):
        def make_components(self):
            base = Box(length=20, width=30, height=15)
            top = Box(length=40, width=20, height=5)
            return {
                'base': base,
                'top': top,
                'fastener': ScrewFastener(parts=[base, top]),
            }

        def make_constraints(self):
            base = self.components['base']
            top = self.components['top']
            fastener = self.components['fastener']
            return [
                Fixed(base.mate_bottom),
                Coincident(top.mate_bottom, base.mate_top),
                Coincident(fastener.mate_origin, top.mate_top),
            ]

Resulting in::

    thing = Thing()
    display(thing)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/fastener-screw/thing.html"
        height="300px" width="100%"
    ></iframe>

.. figure:: img/screw-01.png

    FreeCAD's render may be more clear (literally).
