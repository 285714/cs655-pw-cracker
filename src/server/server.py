import sys
import socket
import argparse
import math
from multiprocessing import Pool
from workers import WORKERS

SOCKET_AMOUNT = 100
MAX_RANGE = 52**5

def read_until_newline(s):
    msg = ""
    while "\n" not in msg:
        msg += s.recv(1024).decode()
    assert(msg.index("\n") + 1 == len(msg))
    return msg[:-1]

def connect_worker(sock, x, y, hash, worker_delay=0):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((hostname, port))
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

def parition_job(worker_list, n): # to change
    assert(len(worker_list) >= n)
    assigned_workers = []
    per_worker = int(math.ceil(MAX_RANGE/n))
    for i in range(n):
        hostname, port = worker_list[i]
        x = i*per_worker
        y = min(MAX_RANGE, (i+1)*per_worker)
        assigned_workers.append((hostname, port, x, y))
    return assigned_workers

def map_reduce(worker_list, hash, n):
    sockets = []
    processes = []
    assigned_workers = parition_job(worker_list, n)
    output = ""
    pool = Pool()
    for (hostname, port, x, y) in assigned_workers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        processes.append(pool.apply_async(connect_worker, (sock, x, y, hash)))
    while True:
        for i, f in enumerate(processes):
            if f.ready() and f.successful() and len(f.get()) == 5:
                output = f.get()
                break
        if output != "" and len(output) == 5:
            break
    pool.close()
    pool.terminate()
    pool.join()
    for sock in sockets:
        try:
            sock.sendall(str.encode("Stop\n"))
            sock.close()
        except Exception as e:
            print(e)
        finally:
            socket.close()
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('--port', type=int, required=True)
    # parser.add_argument('--hostname', type=str, required=True)
    # parser.add_argument('--x', type=int, required=True)
    # parser.add_argument('--y', type=int, required=True)
    parser.add_argument('--hash', type=str, required=True)

    args = parser.parse_args()
    output = map_reduce(WORKERS, args.hash, 2)
    print(output)
