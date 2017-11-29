
from ..params import NonNullParameter


class FreeCADRenderProperties(object):
    """
    Container for freecad rendering properties.

    A simple container for the properties:

    * ``color`` : a 3-tuple representing ``(<red>, <green>, <blue>)``, each
      value in the range: ``{0 <= val <= 255}``
    * ``alpha`` : a float in the range ``{0 <= val <= 1}`` where 0
      is invisible, and 1 is opaque.
    """

    def __init__(self, color=(200, 200, 200), alpha=1):
        self.color = color
        self.alpha = max(0., min(float(alpha), 1.))

    @property
    def transparency(self):
        """
        :return: transparency value, 1 is invisible, 0 is opaque
        :rtype: :class:`float`
        """
        return 1. - self.alpha

    @property
    def rgba(self):
        """
        Red, Green, Blue, Alpha

        :return: red, green, blue, alpha values
        :rtype: :class:`tuple`

        .. doctest::

            >>> from cadquery.utils.freecad_render import FreeCADRenderProperties
            >>> fcrp = FreeCADRenderProperties(color=(1,2,3), alpha=0.2)
            >>> fcrp.rgba
            (1, 2, 3, 0.2)
        """
        return self.color + (self.alpha,)

    @property
    def rgbt(self):
        """
        Red, Green, Blue, Transparency

        :return: red, green, blue, transparency values
        :rtype: :class:`tuple`

        .. doctest::

            >>> from cadquery.utils.freecad_render import FreeCADRenderProperties
            >>> fcrp = FreeCADRenderProperties(color=(1,2,3), alpha=0.2)
            >>> fcrp.rgbt
            (1, 2, 3, 0.8)
        """
        return self.color + (self.transparency,)


class FreeCADRender(NonNullParameter):
    """
    Properties for rendering in FreeCAD.

    This class provides a :class:`FreeCADRenderProperties` instance
    as a :class:`Parameter <cqparts.params.Parameter>` for a
    :class:`ParametricObject <cqparts.params.ParametricObject>`.

    .. doctest::

        >>> from cqparts.params import ParametricObject
        >>> from cqparts.utils.freecad_render import FreeCADRender, TEMPLATE, COLOR
        >>> class Thing(ParametricObject):
        ...     _fc_render = FreeCADRender(TEMPLATE['red'], doc="render params")
        >>> thing = Thing()
        >>> thing._fc_render.color
        (255, 0, 0)
        >>> thing._fc_render.alpha
        1.0
        >>> thing = Thing(_fc_render={'color': COLOR['green'], 'alpha': 0.5})
        >>> thing._fc_render.color
        (0, 255, 0)
        >>> thing._fc_render.alpha
        0.5

    The ``TEMPLATE`` and ``COLOR`` dictionaries provide named templates to
    display your creations quickly, but you can also provide custom properties.
    """

    _doc_type = ':class:`FreeCADRender <cqparts.utils.freecad_render.FreeCADRender>`'

    def type(self, value):
        return FreeCADRenderProperties(**value)


# Templates (may be used optionally)
COLOR = {
    # primary colours
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'yellow': (255, 255, 0),

    # woods
    'wood_light': (235, 152, 78),
    'wood': (235, 152, 78),  # == wood_light
    'wood_dark': (169, 50, 38),

    # metals
    'aluminium': (192, 192, 192),
    'aluminum': (192, 192, 192),  # == aluminium
    'steel': (84, 84, 84),
    'steel_blue': (35, 107, 142),
    'copper': (184, 115, 51),
    'silver': (230, 232, 250),
    'gold': (205, 127, 50),
}

TEMPLATE = dict(
    (k, {'color': v, 'alpha': 1})
    for (k, v) in COLOR.items()
)
TEMPLATE.update({
    'default': {'color': COLOR['aluminium'], 'alpha': 1.0},
    'glass': {'color': (200, 200, 255), 'alpha': 0.2},
})
