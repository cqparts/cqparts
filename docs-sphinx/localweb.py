# run using:
#   ./go.sh web

import os
import time
import SimpleHTTPServer
import SocketServer
import threading
import webbrowser

PORT = 9040
SocketServer.TCPServer.allow_reuse_address = True

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

os.chdir('./_build/html/')
httpd = SocketServer.ThreadingTCPServer(("", PORT), Handler)


print("serving: http://localhost:%i/" % PORT)
try:
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    webbrowser.open("http://localhost:%i/" % PORT)

    while True:  # wait for Ctrl+C
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[keyboard interrupt]")

finally:
    httpd.shutdown()
    httpd.server_close()
    server_thread.join()
    print("[http shutdown successfully]")
