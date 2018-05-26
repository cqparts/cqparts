
__all__ = [
    'render_props',
    'RenderProps', 'RenderParam',

    # display
    'display',

    # environment
    'environment',
]

import functools

# material
from .material import RenderProps, RenderParam
from .material import render_props

# envionrment
from . import environment

# Specific Environments
from .freecad import FreeCADDisplayEnv
from .web import WebDisplayEnv
from .cqparts_server import CQPartsServerDisplayEnv


# Generic display funciton
def display(component, **kwargs):
    """
    Display the given component based on the environment it's run from.
    See :class:`DisplayEnvironment <cqparts.display.environment.DisplayEnvironment>`
    documentation for more details.

    :param component: component to display
    :type component: :class:`Component <cqparts.Component>`

    Additional parameters may be used by the chosen
    :class:`DisplayEnvironment <cqparts.display.environment.DisplayEnvironment>`
    """

    for disp_env in environment.display_environments:
        if disp_env.condition():
            return disp_env.display(component, **kwargs)

    raise LookupError('valid display environment could not be found')
