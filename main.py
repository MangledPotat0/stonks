"""
This script polls the Yahoo Finance API for stock data and writes it to a csv
dump. The script is intended to be run in a docker container and requires a
parameters.json file to be mounted to the container's workdir. The parameters
file should contain a list of tickers to poll.
"""

import csv
import json
import os
import time
from pathlib import Path

import yfinance as yf

# Constants
API_CALL_LIMIT_PER_HOUR = 400 # Yahoo Finance API call limit per hour
SECONDS_PER_HOUR = 3600
WORKDIR_PATH = Path("/app/workdir") # Path to the workdir in the container

def info_to_csv(path, now, ticker_info):
    """
    Parses ticker data dict from yahoo finance API call and writes it to a csv
    file. If the file does not exist, it will be created. If the file does
    exist, the data will be appended to the file.

    Args:
        ticker_info (dict): A dictionary containing ticker data from the Yahoo
            Finance API.

    Returns:
        None
    """

    keys = ticker_info.keys()
    filename = time.strftime(f"{ticker_info['symbol']}%Y%m%d.csv",
                             time.gmtime(now))
    timestamp = time.strftime("%H%M%S", time.gmtime(now))
    ticker_info["timestamp"] = now
    
    if os.path.isfile(path/filename):
        with open(path/filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys, restval="NA")
            writer.writerow(ticker_info)
    else:
        with open(path/filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys, restval="NA")
            writer.writeheader()
            writer.writerow(ticker_info)
    print(ticker_info["symbol"])

def market_is_open():
    currentHour = int(time.strftime("%H", time.gmtime(time.time())))
    return ((12 < currentHour) & (21 > currentHour))

if __name__ == "__main__":
    polling_frequency = API_CALL_LIMIT_PER_HOUR / SECONDS_PER_HOUR
    sleep_time = 1 / polling_frequency

    with open("/app/workdir/parameters.json", 'r') as f:
        params = json.load(f)

    while True:
        if market_is_open():
            for ticker in params["tickers"]:
                now = time.time()
                stonk = yf.Ticker(ticker)
                info_to_csv(WORKDIR_PATH, now, stonk.info)
                time.sleep(sleep_time)
        else:
            timenow = time.strftime("%y-%m-%d-%H:%M:%S",
                                    time.gmtime(time.time())
            )
            print(f"pulse... {timenow}")
            time.sleep(sleep_time)
