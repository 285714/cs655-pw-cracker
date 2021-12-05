import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from multiprocessing import Pool, Manager, Process
import json
import os
import socket

sys.path.append('../src/server')
from server import solve, solved_hashes


hostName = socket.gethostname()
if not hostName.startswith("server"): hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    sessions = {}

    def do_GET(self):
        path = self.path.strip("/").split("/")
        ip = self.client_address[0]

        if path[0] == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "r") as f:
                self.wfile.write(bytes(f.read(), "utf-8"))

        elif path[0] == "crack":
            md5hash = urllib.parse.unquote(path[1]) if len(path) > 1 else None
            num_workers = int(path[2]) if len(path) > 2 else None
            if md5hash is not None:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                if ip not in self.sessions:
                    self.sessions[ip] = []
                self.sessions[ip].append(md5hash)
                print("webserver: forwarding request for {} on {} workers".format(md5hash, num_workers))
                solve(md5hash, num_workers)
            else:
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()

        elif path[0] == "delta":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            print("< <", solved_hashes)
            unsolved_hashes = self.sessions[ip] if ip in self.sessions else []
            now_solved = { hash: solved_hashes[hash]
                    for hash in unsolved_hashes if hash in solved_hashes }
            self.sessions[ip] = [ hash for hash in unsolved_hashes
                    if hash not in now_solved.keys() ]
            self.wfile.write(bytes(json.dumps(now_solved), "utf-8"))

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><body>404 Not found</body></head>", "utf-8"))

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
