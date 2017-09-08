# This is a CadQuery script template
# Add your script code below
import cadquery as cq
from Helpers import show

import sys
sys.path.append('/home/nymphii/workspace/cqparts/src')
from cqparts.part import Pulley, Part

from remote_pdb import RemotePdb
RemotePdb('localhost', 4444).set_trace()

part = Part()
pulley = Pulley()

# Use the following to render your model with grey RGB and no transparency
show(pulley.obj, (204, 204, 204, 0.0))
