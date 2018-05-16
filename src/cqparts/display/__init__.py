
__all__ = [
    'render_props',
    'RenderProps', 'RenderParam',

    # Display function mapping
    'display_map',  # FIXME
    'register_display',  # FIXME

    # display
    'display',
    
    # environment
    'environment',
]

import functools

# material
from .material import RenderProps, RenderParam
from .material import render_props

# environments
from .freecad import FreeCADDisplayEnv
from .web import WebDisplayEnv


# Generic display funciton
def display(component):
    """
    Display the given component based on the
    :meth:`get_env_name() <cqparts.utils.env.get_env_name>`.
    """
    env_name = get_env_name()

    if env_name not in display_map:
        raise KeyError(
            "environment '%s' has no mapped display method" % (env_name)
        )

    return display_map[env_name](component)
