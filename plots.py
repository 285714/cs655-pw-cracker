import subprocess
import re
import sys
import hashlib
import time
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

sys.path.append('./src/server')
from server import solve

data = []
for i in range(5):
    delay = 0.0
    for d in ["AAAAA", "AAaAW", "BBBBB", "AAWAW", "AAAaa"]:
        denc = d.encode('utf-8')
        hash = hashlib.md5(denc).hexdigest()
        start_time = time.time()
        result1 = solve(hash, i + 1)
        delay += time.time() - start_time
        print(denc, delay)
        data.append((i + 1, delay))


df = pd.DataFrame(data, columns=['i', "Cracking Time"])
print(df)

means = df.groupby('i').mean()
print("----")
print(means)
print("----")

x = df["i"].unique()
fig, ax = plt.subplots()

plt.xlabel("Number of workers")
plt.ylabel("Average cracking time")
ax.plot(x, means)
plt.show()
