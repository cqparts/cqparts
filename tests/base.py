import unittest
import sys
import os
import inspect
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(_this_path, '..', 'src'))

class CQPartsTest(unittest.TestCase):

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr))

    def assertEqualAndType(self, obj, exp, t):
        self.assertEqual(obj, exp)
        self.assertEqual(type(exp), t)  # explicit test; intentionally not isinstance()
