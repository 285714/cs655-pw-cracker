import sys
import socket
import argparse

SOCKET_AMOUNT = 100

def read_until_newline(s):
    msg = ""
    while "\n" not in msg:
        msg += s.recv(1024).decode()
    assert(msg.index("\n") + 1 == len(msg))
    return msg[:-1]

def connect_worker(hostname, port, x, y, hash, worker_delay=0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))
    output = "Not Found"
    try:
        # sock.settimeout(worker_delay + 1)
        sock.sendall(str.encode("Connection\n"))
        result = read_until_newline(sock)
        assert(result == "200 OK: Ready")

        sock.sendall(str.encode("Compute {} {} {}\n".format(x,y,hash)))
        while True:
            msg = read_until_newline(sock)
            if len(msg) == 5:
                output = msg
                break
            elif msg.startswith("Not Found"):
                y_ = int(msg.split()[-1])
                if y_ >= y-1:
                    break
            else:
                break
        sock.sendall(str.encode("Stop\n"))
        sock.close()
    except Exception as e:
        print(e)
    finally:
        sock.close()
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--hostname', type=str, required=True)
    parser.add_argument('--x', type=int, required=True)
    parser.add_argument('--y', type=int, required=True)
    parser.add_argument('--hash', type=str, required=True)

    args = parser.parse_args()
    output = connect_worker(args.hostname, args.port, args.x, args.y, args.hash)
    print(output)
