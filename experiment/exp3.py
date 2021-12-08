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
import pandas as pd
import matplotlib.pyplot as plt
import os.path


"""
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
"""

csvfile = "exp3data.csv"

if not os.path.isfile(csvfile):
    num_workers = 2

    df = pd.DataFrame(columns=["lam", "hash", "start_time", "time"])

    start_time = time.time()
    if __name__ == "__main__":
        for lam in [2, 3, 4]:
            for _ in range(10):
                next_solve_time = np.random.poisson(lam=3)
                time.sleep(next_solve_time)

                ix = np.random.randint(0,MAX_RANGE)
                pw = search.convert_order_to_string(ix)
                # prefix = ["AA", "RA", "iA"][np.random.choice(3)]
                prefix = ["AA", "aA"][np.random.choice(2)]
                pw = prefix + pw[:3]
                h = hashlib.md5(pw.encode()).hexdigest()
                df = df.append({"lam":3, "hash": h, "start_time": time.time() - start_time, "time": -1},
                        ignore_index=True)
                solve(h, num_workers)

                print("Beep")
                print(df)
                for h, (_, t) in solved_hashes.items():
                    df.loc[df["hash"] == h, "time"] = t
                # print(solved_hashes)
        # time.sleep(5)

    df = df.loc[df["time"] > 0]
    print(df)
    df.to_csv(csvfile)


df = pd.read_csv(csvfile)

plt.scatter(df["start_time"], df["time"], c="red", alpha=0.5)
plt.show()


"""
    with open("average_time_pwd", 'w') as f:
        f.write("num_workers,password,hash,runtime\n")
    for i in range(10):
        start_index = np.random.randint(0,MAX_RANGE)
        print(i)
        for num_workers in range(1,6):
            pwds, hashes, runtime = measure_average_delay_single_request(start_index, 1, num_workers)
            with open("average_time_pwd", 'a') as f:
                f.write(str(num_workers) + ','+str(pwds[0]) + ',' +str(hashes[0]) + ',' +str(runtime[0]) + "\n")
"""

