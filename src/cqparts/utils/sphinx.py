"""
This module is only to be referenced from your project's sphinx autodoc
configuration.

http://www.sphinx-doc.org/en/stable/ext/autodoc.html
"""

from ..params import ParametricObject


def _add_lines(lines, new_lines, prepend=False, separator=True):
    # Adding / Removing Lines:
    #   sphinx callbacks require the passed ``lines`` parameter to have it's
    #   initial ``id(lines)``, so doing things like ``lines = ['new thing'] + lines``
    #   changes it's ``id`` (allocating new memory), and the new lines list is
    #   forgotten and garbage collected (... sigh).
    #
    #   So the only way to *prepend* / *append* text to the ``lines`` parameter is
    #   to use ``lines.insert(0, new_line)`` / ``lines.append(new_line`` respectively.
    #
    #   To remove lines, use ``del lines[0]``
    #
    #   If in doubt: ``id(lines)`` should return the same number at the start, and
    #   end of the function call.
    has_original_content = bool(lines)
    if prepend:
        # add to the beginning of __doc__
        for (i, new_line) in enumerate(new_lines):
            lines.insert(i, new_line)
        if separator and (new_lines and has_original_content):
            # add blank line between newly added lines and original content
            lines.insert(len(new_lines), '')
    else:
        # append to the end of __doc__
        if separator and (new_lines and has_original_content):
            # add blank line between newly added lines and original content
            lines.append('')
        for new_line in new_lines:
            lines.append(new_line)


def _cls_name(cls):
    return "{}.{}".format(cls.__module__, cls.__name__)


def add_parametric_object_params(prepend=False):
    """
    Add ParameticObject parameters in a table to the *docstring*

    This is only intended to be used with *sphinx autodoc*

    In your *sphinx* ``config.py`` file::

        from cqparts.utils.sphinx import add_parametric_object_params
        def setup(app):
            app.connect("autodoc-process-docstring", add_parametric_object_params())

    Then, when documenting your :class:`Part <cqparts.part.Part>` or
    :class:`Assembly <cqparts.part.Assembly>` the
    :class:`ParametricObject <cqparts.params.ParametricObject>` parameters
    will also be documented in the output.

    :param prepend: If truthy, parameters are added to the beginning of the *docstring*.
                    otherwise, they're appended at the end.
    :type prepend: bool
    """
    def param_lines(app, obj):
        params = ParametricObject._get_class_params(obj)  # list of names

        # Header
        doc_lines = []
        if params:  # only add a header if it's relevant
            doc_lines += [
                ".. tip::",
                "",
                "    This class is a :class:`ParametricObject <cqparts.params.ParametricObject>`",
                "",
                "    That means the following parameters can be set in the constructor.",
                "",
            ]

        # Add parameters
        for key in sorted(params):
            param_def = getattr(obj, key)
            doc_lines.append(':param {name}: {doc}'.format(
                name=key, doc=param_def._param(),
            ))
            doc_lines.append(':type {name}: {doc}'.format(
                name=key, doc=param_def._type(),
            ))

        return doc_lines

    # Conditions for running above `param_lines` function (in order)
    conditions = [  # (all conditions must be met)
        lambda o: type(o) == type,
        lambda o: o is not ParametricObject,
        lambda o: issubclass(o, ParametricObject),
    ]

    def callback(app, what, name, obj, options, lines):
        # sphinx callback
        # (this method is what actually gets sent to the sphinx runtime)
        if all(c(obj) for c in conditions):
            new_lines = param_lines(app, obj)
            _add_lines(lines, new_lines, prepend=prepend)

    return callback
