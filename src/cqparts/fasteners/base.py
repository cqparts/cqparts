import six

from ..part import Part
from ..params import *

# Types of things... not parts on their own, but utilised in many
from ..types import fastener_heads
from ..types import screw_drives
from ..types import threads

# --------- Custom Parameter types ---------
class FastenerComponentParam(Parameter):
    name = None
    finder_callback = None
    component_base = None

    def type(self, value):
        if isinstance(value, self.component_base):
            # component's instance explicitly provided.
            return value

        elif isinstance(value, (tuple, list)):
            # split value
            if len(value) != 2:
                raise ParameterError("given tuple must have 2 elements ({name}_type, dict(params)): {val!r}".format(
                    name=self.name, val=value
                ))
            (component_type, params) = value

            # Get component's class (or raise an exception trying)
            component_class = None
            if type(component_type) is type:  # given value is a class
                if issubclass(component_type, self.component_base):
                    # component class is explicitly defined
                    component_class = component_type
                else:
                    raise ParameterError(
                        "given {name} type class {cls!r} does not inherit from {base!r}".format(
                            name=self.name, cls=type(component_type), base=self.component_base
                        )
                    )
            elif isinstance(component_type, six.string_types):
                # name of component type given, use callback to find it
                try:
                    component_class = self.finder_callback(component_type)
                except ValueError as e:
                    raise ParameterError(
                        ("{name} type of '{type}' cannot be found. ".format(name=self.name, type=component_type)) +
                        "is it spelt correctly (case sensitive)?, has the library defining it been imported?"
                    )
            else:
                raise ParameterError(
                    "{name} type {val!r} must be a str, or a class inheriting from {base!r}".format(
                        name=self.name, val=component_type, base=self.component_base
                    )
                )

            # Verify parameters (very loosely)
            if not isinstance(params, dict):
                raise ParameterError("parameters must be a dict: {!r}".format(params))

            # Create instance & return it
            return component_class(**params)


class HeadType(FastenerComponentParam):
    """
    Fastener's head can be set as any of:
        - FastenerHead instance
        - tuple: (<head type>, <parameters>) where:
            <head type> is one of
                - str: name of fastener head (registered with fastener_heads.fastener_head)
                - FastenerHead subclass
            <parameters> is a dict
    """
    name = 'head'
    finder_callback = staticmethod(fastener_heads.find)
    component_base = fastener_heads.FastenerHead


class DriveType(FastenerComponentParam):
    name = 'drive'
    finder_callback = staticmethod(screw_drives.find)
    component_base = screw_drives.ScrewDrive


class ThreadType(FastenerComponentParam):
    name = 'thread'
    finder_callback = staticmethod(threads.find)
    component_base = threads.Thread


# ----------------- Fastener Base ---------------

class Fastener(Part):
    head = HeadType((
        'pan', {
            'diameter': 5.2,
            'height': 2.0,
            'fillet': 1.0,
        }
    ))
    drive = DriveType((
        'phillips', {
            'diameter': 3,
            'depth': 2.0,
            'width': 0.6,
        }
    ))
    thread = ThreadType((
        threads.iso_262.ISO262Thread, {
            'radius': 3.0 / 2,
            #'pitch': 0.35,  # FIXME: causes invalid thread (see issue #1)
            'pitch': 0.7,
        }
    ))
    length = PositiveFloat(4.5)

    def make(self):
        # build Head
        obj = self.head.make()

        # build Thread (and union it to to the head)
        thread = self.thread.make(self.length + 0.01)
        thread = thread.translate((0, 0, -self.length))
        #return thread  # FIXME
        obj = obj.union(thread)

        # apply screw drive (if there is one)
        if self.drive:
            obj = self.drive.apply(
                obj,
                offset=self.head.get_face_offset()
            )

        return obj

    #def make_cutting_tool(
