
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
        >>> from cqparts.display import RenderProperties, TEMPLATE, COLOR
        >>> class Thing(ParametricObject):
        ...     _fc_render = RenderProperties(TEMPLATE['red'], doc="render params")
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


def render_props(**kwargs):
    """
    Return a valid property for cleaner referencing in :class:`Part <cqparts.part.Part>`
    child classes.

    :param template: name of template to use (any of ``TEMPLATE.keys()``)
    :type template: :class:`str`
    :param doc: description of parameter for sphinx docs
    :type doc: :class:`str`

    :return: render property instance
    :rtype: :class:`RenderProperties`

    .. doctest::

        >>> import cadquery
        >>> from cqparts.display import render_props
        >>> import cqparts
        >>> class Box(cqparts.Part):
        ...     # let's make semi-transparent aluminium (it's a thing!)
        ...     _render = render_props(template='aluminium', alpha=0.8)
        >>> box = Box()
        >>> box._render.rgba
        (192, 192, 192, 0.8)

    The tools in :mod:`cqparts.display` will use this colour and alpha
    information to display the part.
    """
    # Pop named args
    template = kwargs.pop('template', None)
    doc = kwargs.pop('doc', "render properties")

    params = {}

    # Template parameters
    if template in TEMPLATE:
        params.update(TEMPLATE[template])

    # override template with any additional params
    params.update(kwargs)

    # return parameter instance
    return RenderProperties(params, doc=doc)


# -------------------- Render helpers --------------------
def display(*args, **kwargs):
    """
    This displays the given *component(s)* in whatever medium best suits the
    environment.

    For example, if it's called from a FreeCAD script, then the given *component(s)*
    are displayed using FreeCAD's GUI.

    .. warning::

        TODO: document...

        * parameters
        * supported display environments
    """
    from .part import Part, Assembly
    from Helpers import show

    def inner(obj):
        if isinstance(obj, Part):
            # FIXME: only shows local object
            show(obj.local_obj, obj._render.rgbt)
        elif isinstance(obj, Assembly):
            for component in obj.components:
                inner(component)

    inner(*args, **kwargs)
