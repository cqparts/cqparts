import unittest
import sys
import os
import inspect
from collections import defaultdict
from copy import copy

_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', 'src'))

from cqparts import codec


# ------------------- TestCase labels -------------------
def testlabel(*labels):
    """
    Usage::

        @testlabel('quick')
        class MyTest(unittest.TestCase):
            def test_foo(self):
                pass
    """
    def inner(cls):
        # add labels to class
        cls._labels = set(labels) | getattr(cls, '_labels', set())

        return cls

    return inner


# ------------------- Skip Logic -------------------
def skip_if_no_freecad():
    import cadquery

    reason = "freecad 'Helpers.show' could not be imported"

    try:
        from Helpers import show
    except ImportError:
        # freecad import problem, skip the test
        return (True, reason)
    return (False, reason)


class suppress_stdout_stderr(object):
    """
    Suppress stdout & stderr from any process::

        >>> from base import suppress_stdout_stderr
        >>> with suppress_stdout_stderr():
        ...     print("can't see me")

    a copy of: cadquery.freecad_impl.suppress_stdout_stderr
    """
    def __init__(self):
        # Open null files
        self.null_stdout = os.open(os.devnull, os.O_RDWR)
        self.null_stderr = os.open(os.devnull, os.O_RDWR)

        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.saved_stdout = os.dup(1)
        self.saved_stderr = os.dup(2)

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_stdout, 1)
        os.dup2(self.null_stderr, 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.saved_stdout, 1)
        os.dup2(self.saved_stderr, 2)

        # Close all file descriptors
        os.close(self.null_stdout)
        os.close(self.null_stderr)
        os.close(self.saved_stdout)
        os.close(self.saved_stderr)


# ------------------- Core TestCase -------------------

class CQPartsTest(unittest.TestCase):

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr))

    def assertEqualAndType(self, obj, exp, t):
        self.assertEqual(obj, exp)
        self.assertEqual(type(exp), t)  # explicit test; intentionally not isinstance()


class CodecRegisterTests(CQPartsTest):
    def setUp(self):
        super(CodecRegisterTests, self).setUp()
        # Retain mapping
        self.orig_exporter_index = codec.exporter_index
        self.orig_importer_index = codec.importer_index

        # Set Mapping
        codec.exporter_index = defaultdict(dict)
        codec.importer_index = defaultdict(dict)

    def tearDown(self):
        super(CodecRegisterTests, self).tearDown()
        # Restore mapping
        codec.exporter_index = self.orig_exporter_index
        codec.importer_index = self.orig_importer_index
