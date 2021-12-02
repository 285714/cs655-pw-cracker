import sys
import socket
import argparse
import math
from multiprocessing import Pool
from workers import WORKERS

SOCKET_AMOUNT = 100
MAX_RANGE = 52**5
INIT_POWER = 100.0
worker_power = []


def init():
    for i in range(len(WORKERS)):
        worker_power.append(INIT_POWER)

def read_until_newline(s):
    try:
        msg = ""
        while "\n" not in msg:
            msg += s.recv(1024).decode()
        assert(msg.index("\n") + 1 == len(msg))
        return msg[:-1]
    except s.timeout as e:
        return

def connect_worker(w, sock, x, y, hash, worker_delay=5):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((hostname, port))
    output = "Not Found"
    try:
        last_y = x
        sock.settimeout(worker_delay)
        sock.sendall(str.encode("Connection\n"))
        result = read_until_newline(sock)
        if result is None:
            worker_power[w] = max(1, math.round(worker_power[worker_order[i]]/2))
            new_worker, new_w = partition_job(WORKERS, last_y, y, 1)
            hostname, port, new_x, new_y = new_worker[0]
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((hostname, port))
            return connect_worker(new_w, new_sock, new_x, new_y, hash, worker_delay)
        else:
            assert(result == "200 OK: Ready")

        sock.sendall(str.encode("Compute {} {} {}\n".format(x,y,hash)))

        while True:
            msg = read_until_newline(sock)
            if msg is None:
                worker_power[w] = max(1, math.round(worker_power[worker_order[i]]/2))
                new_worker, new_w = partition_job(WORKERS, last_y, y, 1)
                hostname, port, new_x, new_y = new_worker[0]
                new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_sock.connect((hostname, port))
                return connect_worker(new_w, new_sock, new_x, new_y, hash, worker_delay)
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
        worker_power[w] = min(INIT_POWER, worker_power[w]+1)
        sock.close()
    except Exception as e:
        print(e)
        if last_y < y:
            worker_power[w] = max(1, math.round(worker_power[worker_order[i]]/2))
            new_worker, new_w = partition_job(WORKERS, last_y, y, 1)
            hostname, port, new_x, new_y = new_worker[0]
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((hostname, port))
            return connect_worker(new_w, new_sock, new_x, new_y, hash, worker_delay)
    finally:
        sock.close()
    return output

def partition_job(worker_list, start, end, n): # to change
    assert(len(worker_list) >= n)
    worker_order = [w[0] for w in sorted(enumerate(worker_power), key=lambda x:x[1])]
    assigned_workers = []
    per_worker = int(math.ceil((end-start)/n))
    for i in range(n):
        hostname, port = worker_list[worker_order[i]]
        x = i*per_worker
        y = min(end, (i+1)*per_worker)
        assigned_workers.append((hostname, port, x, y))
    return assigned_workers, worker_order[:n]

def map_reduce(hash, n):
    sockets = []
    processes = []
    assigned_workers, worker_order = partition_job(WORKERS, 0, MAX_RANGE, n)
    output = ""
    pool = Pool()
    for i in range(n):
        hostname, port, x, y = assigned_workers[i]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        processes.append(pool.apply_async(connect_worker, (worker_order[i], sock, x, y, hash)))
        # decrease the power by 1 when assign the job to the worker
        worker_power[worker_order[i]] = max(1, worker_power[worker_order[i]]-1)
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
    parser.add_argument('--num_workers', type=int, required=True)

    args = parser.parse_args()
    output = map_reduce(args.hash, args.num_workers)
    print(output)
