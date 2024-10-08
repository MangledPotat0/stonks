import csv
import json
from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np

def plot_daily(data, path):

    print(data["symbol"][0])
    timestamp = np.array(data["timestamp"]).astype(float)
    length = len(timestamp)
    newdict = {"Current Price": "currentPrice",
               "Bid": "bid",
               "Ask": "ask",
               "52 Week High": "fiftyTwoWeekHigh",
               "52 Week Low": "fiftyTwoWeekLow",
            }

    for newkey, key in newdict.items():
        try:
            newdict[newkey] = np.array(data[key]).astype(float)
        except KeyError:
            pass

    for key, value in newdict.items():
        try:
            plt.plot(timestamp, value, label=key)
        except:
            pass
    plt.legend()
    plt.xlabel("Time")
    xticks = plt.gca().get_xticks()
    plt.xticklabels = plt.xticks(xticks,
                                 [time.strftime("%H", time.gmtime(x))
                                        for x in xticks]
    )
    plt.ylabel("Change in price (USD)")
    plt.title("Daily price trends")
    day = time.strftime("%y%m%d", time.gmtime(timestamp[0]))
    symbol = data["symbol"][0]
    plt.savefig(path / f"{symbol}_{day}.png")
    plt.close()

def plot_price_change(data, path):

    timestamp = np.array(data["timestamp"]).astype(float)
    price_open = np.array(data["open"]).astype(float)[-1]
    length = len(timestamp)
    newdict = {"Current Price": "currentPrice",
               "Bid": "bid",
               "Ask": "ask",
            }

    for newkey, key in newdict.items():
        try:
            newdict[newkey] = np.array(data[key]).astype(float)
        except KeyError:
            pass

    for key, value in newdict.items():
        try:
            plt.plot(timestamp, price_open-value, label=key)
        except:
            pass
    plt.legend()
    plt.xlabel("Time")
    xticks = plt.gca().get_xticks()
    plt.xticklabels = plt.xticks(xticks,
                                 [time.strftime("%H", time.gmtime(x))
                                        for x in xticks]
    )
    plt.ylabel("Price (USD)")
    plt.title("Daily Price Changes")
    day = time.strftime("%y%m%d", time.gmtime(timestamp[0]))
    symbol = data["symbol"][0]
    plt.savefig(path / f"{symbol}_{day}_change.png")
    plt.close()

if __name__ == "__main__":
    path = Path("/app/workdir")

    with open("/app/workdir/parameters.json", 'r') as f:
        params = json.load(f)

    for symbol in params["tickers"]:
        with open(path / f"{symbol}20241007.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = {}
            for key in reader.fieldnames:
                data[key] = []
            for row in reader:
                for key in reader.fieldnames:
                    if row[key] == "NA":
                        data[key].append(data[key][-1])
                    else:
                        data[key].append(row[key])
            plot_daily(data, path / "plots")
            plot_price_change(data, path / "plots")
