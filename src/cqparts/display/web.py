
import os
import sys
import inspect
import tempfile
import shutil
import jinja2
import time

# web content
import SimpleHTTPServer
import SocketServer
import threading
import webbrowser

import logging
log = logging.getLogger(__name__)

# Get this file's location
_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Set template web-content directory
# note: can be changed prior to calling web_display()
#
#   >>> from cqparts.display import web
#   >>> web.TEMPLATE_CONTENT_DIR = './my/alternative/template'
#   >>> web.web_display(some_thing)
#
# This would typically be used for testing, or development purposes.
TEMPLATE_CONTENT_DIR = os.path.join(_this_path, 'template')

DEFAULT_PORT = 9041
SocketServer.TCPServer.allow_reuse_address = True  # stops crash on re-use of port


def web_display(component, port=None):
    # Parameter defaults
    if port is None:
        port = DEFAULT_PORT

    # Verify Parameter(s)
    from ..part import Component

    if not isinstance(component, Component):
        raise TypeError("given component must be a %r, not a %r" % (
            Component, type(component)
        ))

    # Create temporary file to host files
    temp_dir = tempfile.mkdtemp()
    host_dir = os.path.join(temp_dir, 'html')
    log.info("host temp folder: %s", host_dir)

    # Copy template content to temporary location
    shutil.copytree(TEMPLATE_CONTENT_DIR, host_dir)

    # Export model
    component.exporter('gltf')(
        filename=os.path.join(host_dir, 'model', 'out.gltf'),
        embed=False,
    )

    # Modify templated content
    # index.html
    with open(os.path.join(host_dir, 'index.html'), 'r') as fh:
        index_template = jinja2.Template(fh.read())
    with open(os.path.join(host_dir, 'index.html'), 'w') as fh:
        fh.write(index_template.render(
            model_filename='model/out.gltf',
            # FIXME: change camera based on scale of model (pull from gltf data)
            camera_target='0 0 0',
            camera_pos='0.5 0.5 0.5',
        ))

    try:
        # Start web-service (loop forever)
        server = SocketServer.ThreadingTCPServer(
            server_address=("localhost", port),
            RequestHandlerClass=SimpleHTTPServer.SimpleHTTPRequestHandler,
        )
        server_addr = "http://%s:%i/" % server.server_address
        def thread_target():
            os.chdir(host_dir)
            server.serve_forever()

        log.info("serving: %s", server_addr)
        sys.stdout.flush()
        server_thread = threading.Thread(target=thread_target)
        server_thread.daemon = True
        server_thread.start()

        # Open in browser
        log.info("opening in browser: %s", server_addr)
        sys.stdout.flush()
        webbrowser.open(server_addr)

        # workaround for https://github.com/dcowden/cadquery/issues/211
        import signal
        def _handler_sigint(signum, frame):
            raise KeyboardInterrupt()
        signal.signal(signal.SIGINT, _handler_sigint)

        print("press [ctrl+c] to stop server")
        sys.stdout.flush()
        while True:  # wait for Ctrl+C
            time.sleep(1)

    except KeyboardInterrupt:
        log.info("\n[keyboard interrupt]")
        sys.stdout.flush()

    finally:
        # Stop web-service
        server.shutdown()
        server.server_close()
        server_thread.join()
        print("[server shutdown successfully]")

        # Delete temporary content
        if os.path.exists(os.path.join(host_dir, 'html', 'cqparts-display.txt')):
            # just making sure we're deleting the right folder
            shutil.rmtree(temp_dir)
