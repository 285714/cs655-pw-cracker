# Average response time for one passwords
import time
import hashlib
import sys
sys.path.append('../src/server')
sys.path.append('../src/worker')
# import server
from server import solve, solved_hashes, MAX_RANGE
import search
import multiprocessing
import numpy as np

def measure_average_delay_single_request(start_index, num_trials, num_workers):
    runtime = []
    pwds = []
    hashes = []
    for i in range(start_index, start_index+num_trials):
        pw = search.convert_order_to_string(i)
        print(i, pw)
        h = hashlib.md5(pw.encode()).hexdigest()
        solve(h, num_workers,True)
        print("done")
        runtime.append(solved_hashes[h][1])
        pwds.append(pw)
        hashes.append(h)
    return pwds, hashes, runtime

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
    with open("average_time_pwd", 'w') as f:
        f.write("num_workers,password,hash,runtime\n")
    for i in range(10):
        start_index = np.random.randint(0,MAX_RANGE)
        print(i)
        for num_workers in range(1,6):
            pwds, hashes, runtime = measure_average_delay_single_request(start_index, 1, num_workers)
            with open("average_time_pwd", 'a') as f:
                f.write(str(num_workers) + ','+str(pwds[0]) + ',' +str(hashes[0]) + ',' +str(runtime[0]) + "\n")
