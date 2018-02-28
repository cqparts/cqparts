
.. _cqparts_fastener-built-in_nut-bolt:

.. currentmodule:: cqparts_fasteners.fasteners.nutbolt

Nut & Bolt
--------------

The :class:`NutBoltFastener` fastener penetrates through all the given parts
with the same diameter hole for the bolt to pass through.

The bolt sticks out the end of the last Part, with the nut attached.

.. doctest::

    import cqparts
    from cqparts.constraint import Fixed, Coincident
    from cqparts_fasteners.fasteners.nutbolt import NutAndBoltFastener
    from cqparts_misc.basic.primatives import Box

    class Thing(cqparts.Assembly):
        def make_components(self):
            base = Box(length=20, width=30, height=15)
            top = Box(length=40, width=20, height=5)
            return {
                'base': base,
                'top': top,
                'fastener': NutAndBoltFastener(parts=[base, top]),
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

    thing = Thing()

Resulting in::

    thing = Thing()
    display(thing)

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/fastener-nut-bolt/thing.html"
        height="300px" width="100%"
    ></iframe>

.. figure:: img/nut-bolt-01.png

    FreeCAD's render may be more clear (literally).
