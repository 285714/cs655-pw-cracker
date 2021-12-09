import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


file = sys.argv[1]

df = pd.read_csv(file)
grp = df.groupby("delay")
runtime = grp["runtime"]

x = grp["delay"].first() / 1000
y = runtime.median()
yl = runtime.quantile(0.25)
yr = runtime.quantile(0.75)

plt.plot(x, y)
plt.fill_between(x, yl, yr, alpha=0.3)

plt.xlabel("Average Response Time (seconds)")
plt.ylabel("Delay (seconds)")
plt.show()



