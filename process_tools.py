import numpy as np
import matplotlib.pyplot as plt
import time

def series_stitch(data, key, altkey=None):
    series = np.array([])
    for kvpair in data:
        try:
            series = np.append(series, kvpair[key], axis=0)
        except KeyError:
            if altkey is not None:
                series = np.append(series, kvpair[altkey], axis=0)
            else:
                pass
    if len(series) == 0:
        series = np.array([0])
    
    return series

def date_on_xticks():
    xticks = plt.gca().get_xticks()
    plt.xticklabels = plt.xticks(xticks,
                                 [time.strftime("%y-%m-%d", time.gmtime(x))
                                        for x in xticks]
    )

def hour_on_xticks():
    xticks = plt.gca().get_xticks()
    plt.xticklabels = plt.xticks(xticks,
                                 [time.strftime("%H", time.gmtime(x))
                                        for x in xticks]
    )
