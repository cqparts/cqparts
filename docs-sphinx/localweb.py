# run using:
#   ./go.sh web

import SimpleHTTPServer
import SocketServer

PORT = 9040

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print("serving: http://localhost:%i/_build/html/" % PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()
    print("    [service shutdown]")
