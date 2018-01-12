import unittest
import sys
import os
import inspect
from collections import defaultdict
from copy import copy


_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', 'src'))


class CQPartsTest(unittest.TestCase):

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr))

    def assertEqualAndType(self, obj, exp, t):
        self.assertEqual(obj, exp)
        self.assertEqual(type(exp), t)  # explicit test; intentionally not isinstance()


# ------------------- TestCase labels -------------------
# label_map = {<label>: <set of classes>, ... }
label_map = defaultdict(set)
label_classes = set()


def testlabel(*labels):
    """
    Usage::

        @testlabel('quick')
        class MyTest(unittest.TestCase):
            def test_foo(self):
                pass
    """
    def inner(cls):
        for label in set(labels):  # removes duplicate labels
            label_map[label].add(cls)
        label_classes.add(cls)
        return cls

    return inner


def _tests_with_labels(labels):
    classes = set()
    for label in labels:
        classes |= label_map[label]
    return classes


def _skip_classes(classes):
    for cls in classes:
        if not getattr(cls, '__unittest_skip__', False):
            unittest.skip('labels')(cls)


def apply_label_whitelist(*labels):
    white_classes = _tests_with_labels(labels)
    _skip_classes(label_classes - white_classes)


def apply_label_blacklist(*labels):
    _skip_classes(_tests_with_labels(labels))
