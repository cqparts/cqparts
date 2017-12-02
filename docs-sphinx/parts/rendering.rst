
.. _parts_rendering:

.. currentmodule:: cqparts.display

Rendering
==============

Render Methods
----------------


.. warning::

    At the time of writing this, the only method of display is from within
    freecad using the cadquery plugin and the :meth:`display` method.

Render Properties
------------------

The properties of a solid's render is stored in the a :class:`RenderProps`
instance, stored in the ``_render`` attribute of each :class:`Part <cqparts.part.Part>`
instance.

.. warning::

    At this time the only properties of a render are its colour (RGB) and alpha
    values.
    This may increase in future to support more advanced rendering, for things
    like reflectance, diffusion, ambiance, I don't know, I'm not a graphics guy.

    For progress regarding this, keep an eye on
    `issue #32 <https://github.com/fragmuffin/cqparts/issues/32>`_, and feel free
    to voice your opinion, and/or support there.
