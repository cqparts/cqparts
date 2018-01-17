
from base import CQPartsTest
from base import testlabel

import cadquery

# Units under test
import cqparts
from cqparts.utils import as_part


class TestAsPart(CQPartsTest):

    def test_basic(self):
        @as_part
        def Box(x=1, y=2, z=3):
            return cadquery.Workplane('XY').box(x, y, z)

        box = Box()
        self.assertIsInstance(box, cqparts.Part)
        self.assertIsInstance(box.local_obj, cadquery.Workplane)
