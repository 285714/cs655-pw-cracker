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
import numpy as np

def measure_average_delay_single_request(start_index, num_trials, num_workers):
    runtime = []
    for i in range(start_index, start_index+num_trials):
        p = search.convert_order_to_string(i)
        h = hashlib.md5(p.encode()).hexdigest()
        p = multiprocessing.Process(target=solve, args=(h, num_workers))
        p.start()
        p.join()
        print("done")
        runtime.append(solved_hashes[h][1])
    return runtime

 # helper method to run the multiple delays experiment   
def delay_experiment(start_index, num_trials):
    nums_workers = [1, 2, 3, 4, 5]
    avg_runtime = [] # store different runtime of different no. of workers
    for n in nums_workers:
        runtime = measure_average_delay_single_request(start_index, num_trials, n)
        avg_runtime.append(np.mean(runtime))
    return avg_runtime

def measure_average_delay_multiple_requests(start_index, num_requests, l): # rq arrives according to Poisson(l)
# TODO
    runtime = []
    t = np.random.poisson(l,num_requests)
    hashes = []
    futures = []
    for i in range(start_index, start_index+num_requests):
        p = search.convert_order_to_string(i)
        h = hashlib.md5(p.encode()).hexdigest()
        pr = multiprocessing.Process(target=solve, args=(h,1))
        futures.append(pr)
        pr.start()
        time.sleep(t[i-start_index])
        print(i, t[i-start_index])
    for pr in futures:
        pr.join()
    return solved_hashes

if __name__ == "__main__":
    print(delay_experiment(10000, 8))
    #print(measure_average_delay_multiple_requests(100000,5,5))
