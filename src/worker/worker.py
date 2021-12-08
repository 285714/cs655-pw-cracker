import sys
import socket
import search
import multiprocessing
import argparse

# format of the command line arguments: server.py hostname port
# setting port number to a command line parameter or to the default value 58123
HOST = '0.0.0.0'
# frequency = 10000 # number of steps that the worker sends
intval = 1 # time [seconds] until worker should send some response

"""
Message from the server as follows
1. Connection\n: set up a new connection
2. Compute x y z\n: request to find a string that match the hash z in range [x, y)
3. Stop\n: stop the request and close the connection
"""

def consume(conn, type=str):
    msg = ""
    while True:
        delim = ("\n" in msg and "\n")
        if delim:
            ix = msg.index(delim)
            part = msg[0:ix]
            return type(part)
        else:
            data = conn.recv(1024)
            msg += data.decode()
            # print("received", msg)
            if msg == "": return msg

def search_and_deliver(conn, x, y, hash, intval):
    try:
        c = x
        while c < y:
            r = range(c, y)
            result = search.search(r, hash, intval)
            # print(result)
            if type(result) == int:
                c = result + 1
                # print("Not Found {}\n".format(result))
                conn.sendall("Not Found {}\n".format(result).encode())
            else:
                conn.sendall("{}\n".format(result).encode())
                break
    except Exception as e:
        print(e)

def handle(conn, address):
    try:
        p = None
        while True:
            message = consume(conn)
            # print(">>>", message)
            if message.startswith("Connection"):
                conn.sendall(b"200 OK: Ready\n")
            elif message.startswith("Compute"):
                x, y, hash = message.split()[1:]
                x, y = int(x), int(y)
                p = multiprocessing.Process(
                    target=search_and_deliver,
                    args=(conn, x, y, hash, intval)
                )
                p.start()
            elif message.startswith("Stop") or not message:
                if p is not None:
                    p.terminate()
                    p.join()
                break
                # conn.close()
    except Exception as e:
        print('Error', e)
    finally:
        conn.close()

class Worker(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)
        self.socket.settimeout(10)
        self.socket.setblocking(True)

        while True:
            conn, address = self.socket.accept()
            # print("ACCEPTING")
            process = multiprocessing.Process(
                target=handle, args=(conn, address))
            # process.daemon = True
            process.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=False)
    args = parser.parse_args()
    port = args.port or 58800
    worker = Worker(HOST, port)
    try:
        print('start')
        worker.start()
    except:
        print('something wrong happened, a keyboard break ?')
    finally:
        for process in multiprocessing.active_children():
            process.terminate()
            process.join()
    print('Goodbye')
