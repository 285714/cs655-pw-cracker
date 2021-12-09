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

    for lam in [0.5, 1, 2, 4]:
        for _ in range(5):
            start_time = time.time()
            for _2 in range(20):
                next_solve_time = np.random.poisson(lam=3)
                time.sleep(next_solve_time)

                ix = np.random.randint(0,MAX_RANGE)
                pw = search.convert_order_to_string(ix)
                # prefix = ["AB", "RB", "iB"][np.random.choice(3)]
                prefix = ["AD", "aD"][np.random.choice(2)]
                pw = prefix + pw[:3]
                h = hashlib.md5(pw.encode()).hexdigest()
                df = df.append({"lam":lam, "hash": h, "start_time": time.time() - start_time, "time": -1},
                        ignore_index=True)
                solve(h, num_workers)

                print(df)
                for h, (_, t) in solved_hashes.items():
                    df.loc[df["hash"] == h, "time"] = t
                # print(solved_hashes)

            print("waiting...")
            while np.any(df["time"] < 0):
                time.sleep(1)
                for h, (_, t) in solved_hashes.items():
                    df.loc[df["hash"] == h, "time"] = t
            print("all done!")

    df = df.loc[df["time"] > 0]
    print(df)
    df.to_csv(csvfile)


df = pd.read_csv(csvfile)
fig = plt.figure(figsize=(8, 6))

for lam in pd.unique(df["lam"]):
    print(lam)
    dflam = df.loc[df["lam"] == lam]
    x = dflam["start_time"].to_numpy()
    y = dflam["time"].to_numpy()

    ixs = np.argsort(x)
    x = x[ixs]
    y = y[ixs]

    def func(x, a, b, c):
        return a * np.log(b * x) + c
    popt, _ = curve_fit(func, x, y)
    z = np.arange(0, np.max(df["start_time"]))
    crop = y < 11
    plt.scatter(x[crop], y[crop], s=7, alpha=0.5)
    plt.plot(z, func(z, *popt), label="Po({})".format(lam))

plt.xlabel("Timeline [s]")
plt.ylabel("Response time [s]")

plt.legend()
plt.tight_layout()
plt.show()


