
.. _parts_rendering:

.. currentmodule:: cqparts.display

Rendering
==============

Render Methods
----------------

A render of your model can be observed using the :meth:`display` method.

This will pick how to display a :class:`Part <cqparts.part.Part>` or
:class:`Assembly <cqparts.part.Assembly>` based on the environment in which it's
run (see :meth:`get_env_name <cqparts.utils.env.get_env_name>` for details).

You may also explicitly set how you'd like your model displayed by calling
another display method, such as :meth:`freecad_display`, :meth:`web_display`,
and so on.

Look at :mod:`cqparts.display` for more information, and options.


Rendered Materials
----------------------

Each :class:`Part <cqparts.part.Part>` can be made to look different
based on its material.

A basic render may simply display everything in a grey matt finish, whereas
a more thoroughly designed model may use colours, transparencies, and metalic
finishes to make a model look more impressive.

The properties of a solid's render is stored in the a :class:`RenderProps`
instance, stored in the ``_render`` attribute of each
:class:`Part <cqparts.part.Part>` instance.

.. warning::

    At this time the only properties of a render are its colour (RGB) and alpha
    values.
    This may increase in future to support more advanced rendering, for things
    like reflectance, diffusion, ambiance, I don't know, I'm not a graphics guy.

    For progress regarding this, keep an eye on
    `issue #36 <https://github.com/fragmuffin/cqparts/issues/36>`_, and feel free
    to voice your opinion, and/or support there.
