import os
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np

import process_tools as pt

if __name__ == "__main__":
    path = Path("/app/workdir/calc")
    i = 0
    j = 0
    plt.figure(figsize=(10,8))
    for datafile in os.listdir(path):
        if datafile.split('.')[1] == "csv":
            symbol = datafile.split("adjusted")[0]
            timeseries, adjyield = np.loadtxt(path/datafile)
            plt.plot(timeseries, adjyield, label=symbol)
            i += 1
            if i == 10:
                i = 0
            if i == 0:
                plt.legend()
                pt.date_on_xticks()
                plt.savefig(path/f"yield_comparison_{j}.png")
                plt.close()
                plt.figure(figsize=(10,8))
                j += 1
