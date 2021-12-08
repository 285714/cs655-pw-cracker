# Average response time for one passwords
import time
import hashlib
import sys
sys.path.append('../src/server')
sys.path.append('../src/worker')
# import server
from server import solve, solved_hashes
import search
import multiprocessing

def measure_average_delay_single_request(start_index, num_trials):
    start_index = start_index
    runtime = []
    for i in range(start_index, start_index+num_trials):
        p = search.convert_order_to_string(i)
        h = hashlib.md5(p.encode()).hexdigest()
        p = multiprocessing.Process(target=solve, args=(h, 1))
        p.start()
        # p.join()
        print("done")
        runtime.append(solved_hashes[h][1])
    return runtime

def measure_average_delay_multiple_requests(start_index, num_requests, l): # rq arrives according to Poisson(l)
# TODO
    start_index = start_index
    runtime = []
    for i in range(start_index, start_index+num_requests):
        p = search.convert_order_to_string(i)
        h = hashlib.md5(p.encode()).hexdigest()
        p = multiprocessing.Process(target=solve, args=(h, 1))
        p.start()
        # p.join()
        print("done")
        runtime.append(solved_hashes[h][1])
    return runtime

if __name__ == "__main__":
    print(measure_average_delay_single_request(1000, 100))
