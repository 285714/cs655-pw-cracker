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
import scipy
from scipy.optimize import curve_fit


csvfile = "exp3data.csv"

if not os.path.isfile(csvfile):
    num_workers = 2

    df = pd.DataFrame(columns=["lam", "hash", "start_time", "time"])

    for lam in [2]:
        start_time = time.time()
        for _ in range(10):
            next_solve_time = np.random.poisson(lam=3)
            time.sleep(next_solve_time)

            ix = np.random.randint(0,MAX_RANGE)
            pw = search.convert_order_to_string(ix)
            prefix = ["AB", "RB", "iB"][np.random.choice(3)]
            # prefix = ["AD", "aD"][np.random.choice(2)]
            pw = prefix + pw[:3]
            h = hashlib.md5(pw.encode()).hexdigest()
            df = df.append({"lam":lam, "hash": h, "start_time": time.time() - start_time, "time": -1},
                    ignore_index=True)
            solve(h, num_workers)

            print(df)
            for h, (_, t) in solved_hashes.items():
                df.loc[df["hash"] == h, "time"] = t
            # print(solved_hashes)
    time.sleep(5)

    df = df.loc[df["time"] > 0]
    print(df)
    df.to_csv(csvfile)


df = pd.read_csv(csvfile)
fig = plt.figure(figsize=(8, 6))

for lam in pd.unique(df["lam"]):
    print(lam)
    dflam = df.loc[df["lam"] == lam]
    x = dflam["start_time"]
    y = dflam["time"]
    def func(x, a, b, c):
        return a * np.log(b * x) + c
    plt.scatter(x, y, s=7, alpha=0.5)
    popt, _ = curve_fit(func, x, y)
    plt.plot(x, func(x, *popt), label="Po({})".format(lam))

plt.legend()
plt.show()


