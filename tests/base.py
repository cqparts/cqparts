import unittest
import sys
import os
import inspect
from collections import defaultdict
from copy import copy


_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', 'src'))


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


# ------------------- Core TestCase -------------------

class CQPartsTest(unittest.TestCase):

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr))

    def assertEqualAndType(self, obj, exp, t):
        self.assertEqual(obj, exp)
        self.assertEqual(type(exp), t)  # explicit test; intentionally not isinstance()
