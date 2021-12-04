import sys
import socket
import argparse
import math
from multiprocessing import Pool, Manager, Process
from workers import WORKERS
import os
import time


SOCKET_AMOUNT = 100
MAX_RANGE = 52**5
MAX_POWER = 100.0
MIN_POWER = 1.0

worker_power = "./worker_power"


def init():
    with open(worker_power, 'w') as f:
        for i in range(len(WORKERS)):
            f.write(str(MAX_POWER) + " ")

def listener(q):
    while True:
        print("listener")
        m = q.get()
        with open(worker_power, 'w') as f:
            if m == 'kill':
                break
            for i in range(len(m)):
                f.write(str(m[i]) + " ")
            f.flush()

def update_worker_power(q, w, t):
    with open(worker_power, 'r') as f:
        pw = f.readlines()[0].split()
        pw[w] = str(t(float(pw[w])))
        print("update", pw, w)
        q.put(pw)

def get_next_worker():
    print("get_next_worker")
    with open(worker_power, 'r') as f:
        pw = f.readlines()[0].split()
        workers = [float(i) for i in pw]
        print(workers)
        worker_order = [w[0] for w in sorted(enumerate(workers), key=lambda x:x[1])]
        return worker_order[0]
def penalty_down(x):
    return max(MIN_POWER,round(x/2))

def penalty_new_worker(x):
    return min(MAX_POWER,x-1)

def addback_power(x):
    return max(MIN_POWER,round(x/2))

def read_until_newline(s):
    try:
        msg = s.recv(1024).decode()
        assert(msg.index("\n") + 1 == len(msg))
        return msg[:-1]
    except Exception as e:
        print(e)
        return

def assign_new_worker(q, w):
    if w >= 0 and w < len(WORKERS):
        update_worker_power(q, w, penalty_down)
    new_w = get_next_worker()
    hostname, port = WORKERS[new_w]
    new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_sock.connect((hostname, port))
    update_worker_power(q, new_w, penalty_new_worker)
    return new_w, new_sock

def connect_worker(q, w, sock, x, y, hash, worker_delay=3):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((hostname, port))
    output = "Not Found"
    try:
        last_y = x
        sock.settimeout(worker_delay)
        sock.sendall(str.encode("Connection\n"))
        result = read_until_newline(sock)
        if result is None:
            new_w, new_sock = assign_new_worker(q, w)
            print(w, "down", "assign", new_w)
            return connect_worker(q, new_w, new_sock, last_y, y, hash, worker_delay)

        else:
            assert(result == "200 OK: Ready")

        sock.sendall(str.encode("Compute {} {} {}\n".format(x,y,hash)))

        while True:
            msg = read_until_newline(sock)
            if msg is None:
                new_w, new_sock = assign_new_worker(q, w)
                print(w, "down", "assign", new_w)
                return connect_worker(q, new_w, new_sock, last_y, y, hash, worker_delay)
            elif len(msg) == 5:
                output = msg
                break
            elif msg.startswith("Not Found"):
                last_y = int(msg.split()[-1]) + 1
                if last_y >= y:
                    break
            else:
                break
        sock.sendall(str.encode("Stop\n"))
        update_worker_power(q, w, addback_power)
        sock.close()
    except Exception as e:
        print(e)
        if last_y < y:
            new_w, new_sock = assign_new_worker(q, w)
            print(w, "down", "assign", new_w)
            return connect_worker(q, new_w, new_sock, last_y, y, hash, worker_delay)
    finally:
        sock.close()
    return output

def partition_job(q, start, end, n): # to change
    assert(n <= len(WORKERS))
    assigned_workers = []
    per_worker = int(math.ceil((end-start)/n))

    with open(worker_power, 'r') as f:
        pw = f.readlines()[0].split()
        workers = [float(i) for i in pw]
        worker_order = [w[0] for w in sorted(enumerate(workers), key=lambda x:x[1])]

    for i in range(n):
        x = i*per_worker
        y = min(end, (i+1)*per_worker)
        w = worker_order[i]

        hostname, port = WORKERS[w]
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_sock.connect((hostname, port))
        update_worker_power(q, w, penalty_new_worker)


        assigned_workers.append((w, new_sock, x, y))
    return assigned_workers

def map_reduce(pool, q, hash, n):
    sockets = []
    processes = []
    assigned_workers = partition_job(q, 0, MAX_RANGE, n)
    output = ""
    for i in range(n):
        w, sock, x, y = assigned_workers[i]
        processes.append(pool.apply_async(connect_worker, (q, w, sock, x, y, hash)))
    while True:
        for i, f in enumerate(processes):
            if f.ready() and f.successful() and len(f.get()) == 5:
                output = f.get()
                break
        if output != "" and len(output) == 5:
            break
    # pool.close()
    # pool.terminate()
    # pool.join()
    for sock in sockets:
        try:
            sock.sendall(str.encode("Stop\n"))
            sock.close()
        except sock.error as e:
            print(e)
        finally:
            sock.close()
    return output


init()
pool = Pool()
manager = Manager()
q = manager.Queue()
solved_hashes = manager.dict()
watcher = pool.apply_async(listener, (q,))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
#   parser.add_argument('--port', type=int, required=True)
#   parser.add_argument('--hostname', type=str, required=True)
#   parser.add_argument('--x', type=int, required=True)
#   parser.add_argument('--y', type=int, required=True)
    parser.add_argument('--hash', type=str, required=True)
    parser.add_argument('--num_workers', type=int, required=True)
    args = parser.parse_args()

    solve(args.hash, args.num_workers)
#   output = map_reduce(pool, q, args.hash, args.num_workers)
#   print(output)


def solve_async(hash, num_workers, q, solved_hashes):
    print("solving MD5(?) = {}".format(hash))
    t = time.time()
    output = map_reduce(pool, q, hash, num_workers)
    solved_hashes[hash] = (output, time.time() - t)
    print("solved MD5({}) = {}".format(output, hash))


def solve(hash, num_workers=None):
    num_workers = len(WORKERS) if num_workers is None else num_workers
    p = Process(target=solve_async, args=(hash, num_workers, q, solved_hashes))
    p.start()

