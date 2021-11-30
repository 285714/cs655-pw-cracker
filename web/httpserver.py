from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.strip("/").split("/")

        if path[0] == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "r") as f:
                self.wfile.write(bytes(f.read(), "utf-8"))

        elif path[0] == "crack":
            md5hash = urllib.parse.unquote(path[1])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            print("start working on", md5hash)

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><body>404 Not found</body></head>", "utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

