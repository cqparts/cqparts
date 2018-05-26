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
import tempfile

import logging
log = logging.getLogger(__name__)


ENVVAR_SERVER = 'CQPARTS_SERVER'


def cqpss(component):
    """
    Display given component in a cqps-server window

    :param component: the component to render
    :type component: :class:`Component <cqparts.Component>`
    """
    # Check environmental assumptions
    if ENVVAR_SERVER not in os.environ:
        raise KeyError("environment variable '%s' not set" % ENVVAR_SERVER)

    # Verify Parameter(s)
    # check that it is a component
    from .. import Component
    if not isinstance(component, Component):
        raise TypeError("given component must be a %r, not a %r" % (
            Component, type(component)
        ))

    # create temporary folder
    temp_dir = tempfile.mkdtemp()

    # export the files to the name folder
    exporter = component.exporter('gltf')
    exporter(
        filename=os.path.join(temp_dir, 'out.gltf'),
        embed=False,
    )

    # get the server from the environment
    server_url = os.environ[ENVVAR_SERVER]

    # notify the cq parts server
    payload = {'name' : type(component).__name__}
    resp = requests.post(server_url + '/notify', data=payload)
