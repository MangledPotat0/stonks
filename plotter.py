"""
This script reads in a csv file containing stock data and plots the daily price
trends and price changes for the stock.
"""
import csv
import json
from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np

import business_logic as bs
import process_tools as pt

def plot_daily(data, path):
    """
    Plots the daily price trends for the stock data.

    Args:
        data (dict): A dictionary containing the stock data.
        path (Path): The path to save the plot.
    
    Returns:
        None
    """

    timestamp = np.array(data["timestamp"]).astype(float)
    length = len(timestamp)
    newdict = {"Bid": "bid",
               "Ask": "ask",
               "Current Price": "currentPrice",
               "Open": "open",
            }

    keys = list(newdict.keys())
    values = list(newdict.values())
    for newkey, key in zip(keys, values):
        try:
            newdict[newkey] = np.array(data[key]).astype(float)
        except KeyError:
            if key == "currentPrice":
                del newdict["Current Price"]
                newdict["Midpoint"] = (newdict["Bid"] + newdict["Ask"])/2
            else:
                pass
    
    tradevolume = np.array(data["volume"]).astype(float)
    barwidth = timestamp[::2][1] - timestamp[::2][0]
    tradevolume = tradevolume[::2]
    tradevolume[1:] = tradevolume[1:] - tradevolume[:-1]
    tradevolume[tradevolume < 0] = 0
    tradevolume[0] = 0

    plt.figure(figsize=(12,9))
    plt.plot(timestamp, newdict["Open"], label="Open")
    try:
        plt.plot(timestamp, newdict["Current Price"], label="Current Price")
    except KeyError:
        plt.plot(timestamp, newdict["Midpoint"], label="Midpoint")
    plt.fill_between(timestamp, newdict["Ask"], newdict["Bid"], alpha=0.5,
                     label="Ask-Bid spread")
    plt.ylabel("Change in price (USD)")
    plt.gca().set_ylim(0)
    ax2 = plt.gca().twinx()
    ax2.bar(timestamp[::2], tradevolume, width=barwidth,
            label="Trade Volume", color="red")
    ax2.set_ylim(0, 2*tradevolume.max())
    plt.legend()
    plt.xlabel("Time")
    pt.hour_on_xticks()
    plt.title("Daily price trends")
    day = time.strftime("%y%m%d", time.gmtime(timestamp[0]))
    symbol = data["symbol"][0]
    print(symbol)
    plt.savefig(path / f"{symbol}_{day}.png")
    plt.close()

def plot_price_change(data, path):
    """
    Plots the price changes for the stock data.

    Args:
        data (dict): A dictionary containing the stock data.
        path (Path): The path to save the plot.

    Returns:
        None
    """

    timestamp = np.array(data["timestamp"]).astype(float)
    price_open = np.array(data["open"]).astype(float)[-1]
    length = len(timestamp)
    newdict = {"Bid": "bid",
               "Ask": "ask",
               "Current Price": "currentPrice"
            }

    keys = list(newdict.keys())
    values = list(newdict.values())
    for newkey, key in zip(keys, values):
        try:
            newdict[newkey] = np.array(data[key]).astype(float)
        except KeyError:
            if key == "currentPrice":
                newdict["Current Price"] = data["navPrice"]
            else:
                pass

    plt.figure(figsize=(12,9))
    plt.plot(timestamp, newdict["Current Price"], label="Current Price")
    plt.fill_between(timestamp, newdict["Ask"], newdict["Bid"], alpha=0.5,
                     label="Ask-Bid spread")
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.title("Daily Price Changes")
    pt.hour_on_xticks()
    day = time.strftime("%y%m%d", time.gmtime(timestamp[0]))
    symbol = data["symbol"][0]
    plt.savefig(path / f"{symbol}_{day}_change.png")
    plt.close()


def plot_multiday(datadict, path):
    ticker = datadict[0]["symbol"][0]
    price_open = pt.series_stitch(datadict, "open")
    price_close = pt.series_stitch(datadict, "previousClose")
    current_price = pt.series_stitch(datadict, "currentPrice",
                                     altkey="navPrice")
    timestamp = pt.series_stitch(datadict, "timestamp")

    current_price = current_price.astype(float)
    price_open = price_open.astype(float)
    price_close = price_close.astype(float)
    timestamp = timestamp.astype(float)
    plt.plot(timestamp, price_open, label="Open")
    plt.plot(timestamp, price_close, label="Close")
    plt.ylabel("Price ($)")
    plt.xlabel("Time")
    plt.legend()
    pt.date_on_xticks()
    plt.savefig(path/f"{ticker}_multiday.png")
    plt.close()

    plt.plot(timestamp, current_price, label="Current price")
    plt.ylabel("Price ($)")
    plt.xlabel("Time")
    pt.date_on_xticks()
    plt.savefig(path/f"{ticker}_fullprice.png")
    plt.close()
    print(ticker)
    return

def plot_risk_values(data, path):
    trimmed_data = {}
    trimmed_data["symbol"] = data[0]["symbol"][0]
    trimmed_data["timestamp"] = pt.series_stitch(data, "timestamp"
                                    ).astype(float)
    trimmed_data["current"] = pt.series_stitch(data, "currentPrice",
                                               altkey="navPrice"
                                    ).astype(float)
    trimmed_data["open"] = pt.series_stitch(data, "open"
                                    ).astype(float)
    trimmed_data["close"] = pt.series_stitch(data, "previousClose"
                                    ).astype(float)
    trimmed_data["high52"] = pt.series_stitch(data, "fiftyTwoWeekHigh"
                                    ).astype(float)
    trimmed_data["low52"] = pt.series_stitch(data, "fiftyTwoWeekLow"
                                    ).astype(float)
    trimmed_data["highday"] = pt.series_stitch(data, "dailyHigh"
                                    ).astype(float)
    trimmed_data["lowday"] = pt.series_stitch(data, "dailyLow"
                                    ).astype(float)
    trimmed_data["dividend"] = pt.series_stitch(data, "dividendYield",
                                    ).astype(float)

    r_value = bs.r_value(trimmed_data)
    plt.plot(trimmed_data["timestamp"], r_value)
    pt.date_on_xticks()
    plt.savefig(path/f"{trimmed_data['symbol']}rvalue.png")
    plt.close()

    p_value = bs.p_value(trimmed_data)
    plt.plot(trimmed_data["timestamp"], p_value)
    pt.date_on_xticks()
    plt.savefig(path/f"{trimmed_data['symbol']}pvalue.png")
    plt.close()

    plt.plot(trimmed_data["timestamp"], p_value*trimmed_data["dividend"],
             label="Adjusted yield")
    pt.date_on_xticks()
    plt.savefig(path/f"{trimmed_data['symbol']}adjusted_yield.png")
    plt.close()
    np.savetxt(path/f"{trimmed_data['symbol']}adjusted_yield.csv",
               np.array([trimmed_data["timestamp"],
                        p_value*trimmed_data["dividend"]]))
    return

if __name__ == "__main__":
    path = Path("/app/workdir")

    with open("/app/workdir/parameters.json", 'r') as f:
        params = json.load(f)

    for symbol in params["tickers"]:
        with open(path / f"{symbol}20241008.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = {}
            for key in reader.fieldnames:
                data[key] = []
            for row in reader:
                for key in reader.fieldnames:
                    if row[key] == "NA":
                        try:
                            data[key].append(data[key][-1])
                        except IndexError:
                            data[key].append(0)
                    else:
                        data[key].append(row[key])
            plot_daily(data, path / "plots")
            plot_price_change(data, path / "plots")

    for symbol in params["tickers"]:
        dictseries = []
        for i in range(20):
            i = ("0"+str(i))[-2:]
            try:
                with open(path / f"{symbol}202410{i}.csv", 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    data = {}
                    for key in reader.fieldnames:
                        data[key] = []
                    for row in reader:
                        for key in reader.fieldnames:
                            if row[key] == "NA":
                                try:
                                    data[key].append(data[key][-1])
                                except IndexError:
                                    data[key].append(0)
                            else:
                                data[key].append(row[key])
                    dictseries.append(data)
            except FileNotFoundError:
                pass

        plot_multiday(dictseries, path / "plots")
        plot_risk_values(dictseries, path / "calc")
