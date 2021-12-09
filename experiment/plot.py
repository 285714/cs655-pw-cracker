import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


file = sys.argv[1]

df = pd.read_csv(file)
grp = df.groupby("num_workers")
runtime = grp["runtime"]

x = grp["num_workers"].first()
y = runtime.median()
yl = runtime.quantile(0.25)
yr = runtime.quantile(0.75)

plt.plot(x, y)
plt.fill_between(x, yl, yr, alpha=0.3)

plt.xlabel("Number of workers")
plt.ylabel("Average delay (seconds)")
plt.show()



