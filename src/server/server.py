import sys
import socket
import argparse
import math
from multiprocessing import Pool, Manager, Process
from workers import WORKERS
import os
import time
import numpy as np


SOCKET_AMOUNT = 100
MAX_RANGE = 52**5
MAX_POWER = 100.0
MIN_POWER = 1.0

TIME_TO_RECONNECT = 10
RECONNECT_ATTEMPT = 15

STATUS_ACTIVE = 'active'
STATUS_DOWN = 'down'

worker_power = "./worker_power"


def init():
    with open(worker_power, 'w') as f:
        for i in range(len(WORKERS)):
            f.write(str(MAX_POWER) + " " + STATUS_ACTIVE)
            if i < len(WORKERS)-1:
                f.write("\n")

def listener(q):
    while True:
        m = q.get()
        with open(worker_power, 'w') as f:
            if m == 'kill':
                break
            for i in range(len(m)):
                f.write(str(m[i][0]) + " " + m[i][1])
                if i < len(m)-1:
                    f.write("\n")
            f.flush()

def update_worker_power(q, w, t, u_status):
    with open(worker_power, 'r') as f:
        pw = f.readlines()
        pw_updated = []
        for i in range(len(pw)):
            a, b = pw[i].split()
            pw_updated.append((float(a), b))
        if pw_updated[w][1] == STATUS_DOWN and u_status == STATUS_ACTIVE:
            pw_updated[w] = (t(addback_reconnected_worker(float(pw_updated[w][0]))), u_status)
            # if worker can be reconnect, add back the power
        if pw_updated[w][1] == STATUS_DOWN and u_status == STATUS_DOWN:
            pw_updated[w] = (penalty_new_worker(float(pw_updated[w][0])), u_status)
            # ease the penalty
        else:
            pw_updated[w] = (t(float(pw_updated[w][0])), u_status)
        print("update", pw_updated, w)
        q.put(pw_updated)

def get_next_worker():
    lines = []
    try:
        while len(lines) == 0:
            with open(worker_power, 'r') as f:
                lines = f.readlines()
                if len(lines) != 0:
                    workers = np.array([float(l.split()[0]) for l in lines])
                    p_workers = workers/sum(workers)
                    return np.random.choice(len(workers), 1, p=p_workers)[0]
    except Exception as e:
        print(e)
        return np.random.choice(len(WORKERS), 1)[0]
def penalty_down(x):
    return max(MIN_POWER,round(x/2))

def penalty_new_worker(x):
    return max(MIN_POWER,x-1)

def addback_power(x):
    return min(MAX_POWER,x+1)

def addback_reconnected_worker(x):
    return min(MAX_POWER,x*2)

def read_until_newline(s):
    try:
        msg = s.recv(1024).decode()
        assert(msg.index("\n") + 1 == len(msg))
        return msg[:-1]
    except Exception as e:
        print(e)
        return

def assign_new_worker(q, w):
    new_w = 0
    try:
        if w is not None and w >= 0 and w < len(WORKERS):
            update_worker_power(q, w, penalty_down, STATUS_DOWN)
        new_w = get_next_worker()
        hostname, port = WORKERS[new_w]
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_sock.connect((hostname, port))
        update_worker_power(q, new_w, penalty_new_worker, STATUS_ACTIVE)
        return new_w, new_sock
    except Exception as e:
        print(e)
        update_worker_power(q, new_w, penalty_down, STATUS_DOWN)
        return None, None

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
            attempt = 0
            new_w = w
            while True:
                new_w, new_sock = assign_new_worker(q, new_w)
                if new_w is None:
                    attempt += 1
                    print("attempt {} to connect worker".format(attempt))
                    time.sleep(TIME_TO_RECONNECT) #wait for 5 seconds
                if attempt > RECONNECT_ATTEMPT:
                    break
                elif new_w is not None:
                    break
            print(w, "down", "assign", new_w)
            if new_w is not None:
                return connect_worker(q, new_w, new_sock, last_y, y, hash, worker_delay)
            else:
                return "Cannot connect"

        else:
            assert(result == "200 OK: Ready")

        sock.sendall(str.encode("Compute {} {} {}\n".format(x,y,hash)))

        while True:
            msg = read_until_newline(sock)
            if msg is None:
                attempt = 0
                new_w = w
                while True:
                    new_w, new_sock = assign_new_worker(q, new_w)
                    if new_w is None:
                        attempt += 1
                        print("attempt {} to connect worker".format(attempt))
                        time.sleep(TIME_TO_RECONNECT) #wait for 5 seconds
                    if attempt > RECONNECT_ATTEMPT:
                        break
                    elif new_w is not None:
                        break
                print(w, "down", "assign", new_w)
                if new_w is not None:
                    return connect_worker(q, new_w, new_sock, last_y, y, hash, worker_delay)
                else:
                    return "Cannot connect"
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
        update_worker_power(q, w, addback_power, STATUS_ACTIVE)
        sock.close()
    except Exception as e:
        print(e)
        if last_y < y:
            attempt = 0
            new_w = w
            while True:
                new_w, new_sock = assign_new_worker(q, new_w)
                if new_w is None:
                    attempt += 1
                    print("attempt {} to connect worker".format(attempt))
                    time.sleep(TIME_TO_RECONNECT) #wait for 5 seconds
                if attempt > RECONNECT_ATTEMPT:
                    break
                elif new_w is not None:
                    break
            print(w, "down", "assign", new_w)
            if new_w is not None:
                return connect_worker(q, new_w, new_sock, last_y, y, hash, worker_delay)
            else:
                return "Cannot connect"
    finally:
        sock.close()
    return output

def partition_job(q, start, end, n): # to change
    assert(n <= len(WORKERS))
    assigned_workers = []
    per_worker = int(np.ceil((end-start)/n))

    with open(worker_power, 'r') as f:
        pw = f.readlines()
        workers = [float(l.split()[0]) for l in pw]
        worker_order = [w[0] for w in sorted(enumerate(workers), key=lambda x:-x[1])]

    current_partition = 0
    current_worker = 0

    while current_partition < n:
        x = current_partition*per_worker
        y = min(end, (current_partition+1)*per_worker)

        check_status = False
        attempt = 0

        while check_status == False:
            try:
                w = worker_order[current_worker]
                hostname, port = WORKERS[w]
                new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_sock.connect((hostname, port))
                update_worker_power(q, w, penalty_new_worker, STATUS_ACTIVE)
                assigned_workers.append((w, new_sock, x, y))
                check_status = True
                current_partition += 1
                current_worker = (current_worker + 1)%len(WORKERS)
            except Exception as e:
                print(e)
                update_worker_power(q, w, penalty_down, STATUS_DOWN)
                attempt += 1
                if attempt % len(WORKERS) == 0:
                    time.sleep(TIME_TO_RECONNECT)
                current_worker = (current_worker + 1)%len(WORKERS)
                if attempt > RECONNECT_ATTEMPT * len(WORKERS):
                    break
        if check_status == False:
            return # No available workers
    return assigned_workers

def map_reduce(q, hash, n):
    pool = Pool()
    # watcher = pool.apply_async(listener, (q,))

    sockets = []
    processes = []
    assigned_workers = partition_job(q, 0, MAX_RANGE, n)
    if assigned_workers is None:
        return "No available workers"
    output = ""
    for i in range(n):
        w, sock, x, y = assigned_workers[i]
        processes.append(pool.apply_async(connect_worker, (q, w, sock, x, y, hash)))
    while True:
        ready = 0
        for i, f in enumerate(processes):
            if f.ready():
                ready += 1
            if f.ready() and f.successful() and len(f.get()) == 5:
                output = f.get()
                break
        if ready == len(processes):
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
        except Exception as e:
            print(e)
        finally:
            sock.close()
    return output


def solve_async(hash, num_workers, q, solved_hashes):
    init()
    # manager = Manager()
    # solved_hashes = manager.dict()
    # q = manager.Queue()

    print("solving MD5(?) = {} on {} workers".format(hash, num_workers))
    t = time.time()
    output = map_reduce(q, hash, num_workers)
    solved_hashes[hash] = (output, time.time() - t)
    print("solved MD5({}) = {}".format(output, hash))


def solve(hash, num_workers=None):
    if num_workers is None or num_workers > len(WORKERS):
        num_workers = len(WORKERS)
    p = Process(target=solve_async, args=(hash, num_workers, q, solved_hashes))
    p.start()
    p.join()


manager = Manager()
solved_hashes = manager.dict()
q = manager.Queue()

pool = Pool()
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
