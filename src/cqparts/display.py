
#from .part import Part, Assembly  # removed due to circular dependency
from .params import as_parameter


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


# -------------------- Parameter(s) --------------------
@as_parameter(nullable=False)
class RenderProperties(object):
    """
    Properties for rendering.

    This class provides a :class:`RenderProperties` instance
    as a :class:`Parameter <cqparts.params.Parameter>` for a
    :class:`ParametricObject <cqparts.params.ParametricObject>`.

    .. doctest::

        >>> from cqparts.params import ParametricObject
        >>> from cqparts.display import Render, TEMPLATE, COLOR
        >>> class Thing(ParametricObject):
        ...     _fc_render = Render(TEMPLATE['red'], doc="render params")
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

            >>> from cadquery.display import RenderProperties
            >>> fcrp = RenderProperties(color=(1,2,3), alpha=0.2)
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

            >>> from cadquery.display import RenderProperties
            >>> fcrp = RenderProperties(color=(1,2,3), alpha=0.2)
            >>> fcrp.rgbt
            (1, 2, 3, 0.8)
        """
        return self.color + (self.transparency,)


# -------------------- Render helpers --------------------
def display(*args, **kwargs):
    from .part import Part, Assembly
    from Helpers import show

    def inner(obj):
        if isinstance(obj, Part):
            show(obj.object)
        elif isinstance(obj, Assembly):
            for component in obj.components:
                inner(component)

    inner(*args, **kwargs)
