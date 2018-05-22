# generate the files and notify the cqparts server
# look at https://github.com/zignig/cqparts-server
# copied and edited from web.py
# Copyright 2018 Peter Boin
# and Simon Kirkby 2018

import os
import sys
import inspect
import time
import requests

import logging
log = logging.getLogger(__name__)

from ..utils import working_dir

def cqpss(component):
    """
    Display given component in a cqps-server window
    """
    # Verify Parameter(s)
    from .. import Component
    cp_name = component.__class__.__name__
    # linux only for now
    base_dir = "/tmp/cqpss/"
    host_dir = ""
    # make the folders
    try:
        os.mkdir(base_dir)
    except:
       pass 
    try:
        host_dir = os.path.join(base_dir,cp_name)
        os.mkdir(host_dir)
    except:
        pass
    # check that it is a component
    if not isinstance(component, Component):
        raise TypeError("given component must be a %r, not a %r" % (
            Component, type(component)
        ))
    # export the files to the name folder
    exporter = component.exporter('gltf')
    exporter(
        filename=os.path.join(host_dir, 'out.gltf'),
        embed=False,
    )
    # get the server from the environment 
    server_url = os.environ['CQPARTS_SERVER']
    # notify the cq parts server 
    payload = {'name' : cp_name }
    resp = requests.post(server_url+'/notify',data=payload)

