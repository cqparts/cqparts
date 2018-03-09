from base import CQPartsTest
from base import testlabel

# units under test
from cqparts_fasteners.fasteners.nutbolt import NutAndBoltFastener

# ---------- Test Assembly ----------

import cadquery
import cqparts
from partslib.basic import Box
from cqparts import constraint
from cqparts.utils import CoordSystem

class FastenedAssembly(cqparts.Assembly):
    def make_components(self):
        base = Box(length=20, width=20, height=12)
        top = Box(length=18, width=18, height=18)
        return {
            'base': base,
            'top': top,
            'fastener': NutAndBoltFastener(parts=[base, top]),
        }

    def make_constraints(self):
        base = self.components['base']
        top = self.components['top']
        fastener = self.components['fastener']
        return [
            constraint.Fixed(base.mate_bottom),
            constraint.Coincident(top.mate_bottom, base.mate_top),
            constraint.Coincident(fastener.mate_origin, top.mate_top + CoordSystem((1, 2, 0))),
        ]


# ---------- Unit Tests ----------

class ScrewFastenerTest(CQPartsTest):
    def test_fastener(self):
        obj = FastenedAssembly()
        bolt = obj.find('fastener.bolt')
        nut = obj.find('fastener.nut')

        self.assertEquals(bolt.world_coords.origin, cadquery.Vector((1, 2, 30)))
        self.assertGreater(
            bolt.bounding_box.zlen,
            obj.find('top').height + obj.find('base').height
        )
        self.assertEquals(nut.world_coords.origin, cadquery.Vector((1, 2, 0)))
