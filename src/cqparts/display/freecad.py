import cadquery

import logging
log = logging.getLogger(__name__)

from .environment import map_environment, DisplayEnvironment


@map_environment(
    name="freecad",
    order=10,
    condition=lambda: 'MYSCRIPT_DIR' in os.environ,
)
class FreeCADDisplayEnv(DisplayEnvironment):
    def display_callback(self, component):
        """
        Display given component in FreeCAD

        :param component: the component to render
        :type component: :class:`Component <cqparts.Component>`
        """

        from .. import Part, Assembly
        import cadquery
        from Helpers import show

        def inner(obj, _depth=0):
            log.debug("display obj: %r: %r", type(self), obj)
            if isinstance(obj, Part):
                if _depth:
                    # Assembly being displayed, parts need to be placed
                    show(obj.world_obj, obj._render.rgbt)
                else:
                    # Part being displayed, just show in local coords
                    show(obj.local_obj, obj._render.rgbt)

            elif isinstance(obj, Assembly):
                obj.solve()
                for (name, component) in obj.components.items():
                    inner(component, _depth=_depth + 1)

            elif isinstance(obj, cadquery.CQ):
                show(obj)

        inner(component)
