
from .part import Part, Assembly
from Helpers import show

def display(obj):
    if isinstance(obj, Part):
        show(obj.object)
    elif isinstance(obj, Assembly):
        for component in obj.components:
            display(component)
