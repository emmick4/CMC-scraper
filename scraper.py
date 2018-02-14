import requests
import csv
import time
import sys

def call_api(url):
    response = requests.get(url)
    count = 1
    while response.status_code != 200:
        response = requests.get(url)
        count += 1
        time.sleep(0.2)
    return response.json()

def scrape(coin, ts):
    '''

    :param coin: name of coin, according to its coinmarketcap.com url
    :param ts: unix timestamp w/o milliseconds
    :return: array of CMC data
    '''
    #  scrape 24h steps of price data with 5 min granularity
    ts *= 1000  # coinmarketcap wants milliseconds for some reason
    step = 86400000
    url = "https://graphs2.coinmarketcap.com/currencies/bitcoin/{ts}/{ts2}/".format(ts=ts, ts2= ts+step)
    response = call_api(url)
    return response

def parse_output(output):
    '''

    :param output: output from the scrape function
    :return: returns list of dicts [{"ts": ts, "price_usd": price_usd, "price_btc": price_btc, "volume": volume, "mcap": mcap}, ...]
    '''
    ts_table = []
    for i in range(len(output['price_usd'])):
        ts = output['price_usd'][i][0]
        price_usd = output['price_usd'][i][1]
        price_btc = output['price_btc'][i][1]
        volume = output['volume_usd'][i][1]
        mcap = output['market_cap_by_available_supply'][i][1]
        d = {"ts": str(ts), "price_usd": str(price_usd), "price_btc": str(price_btc), "volume": str(volume), "mcap": str(mcap)}
        ts_table.append(d)
    return ts_table

def ts_to_str(ts):
    struct_time = time.gmtime(ts)
    return time.strftime("%m-%d-%Y %H:%M", struct_time)

def name_file(start_time, num_days):
    end_timestamp = start_time + (num_days * 86400)
    start_str = ts_to_str(start_time)
    end_str = ts_to_str(end_timestamp)
    filename = start_str + ' - ' + end_str + ".csv"
    return filename

def grab_data(start_time, num_days, coin):
    times = [start_time + (i * 86400) for i in range(num_days)]
    complete_array = []
    count = 1
    for ts in times:
        print("Scraping Day #", count)
        count += 1
        output = scrape(coin, ts)
        parsed = parse_output(output)
        complete_array.extend(parsed)
    return complete_array, name_file(start_time, num_days)

def write_data(filename, array):
    with open(filename, "w+") as csvfile:
        field_names = ["ts", "price_usd", "price_btc", "volume", "mcap"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(array)


def get_args():
    args = sys.argv
    for arg in args:
        if "start_time=" in arg:
            start_time = int(arg.lstrip("start_time="))
        elif "num_days=" in arg:
            num_days = int(arg.lstrip("num_days="))
        elif "coin=" in arg:
            coin = arg.lstrip("coin=")
    if not num_days:
        num_days = (time.time() - start_time)/86400
    return start_time, num_days, coin

def __main__():
    try:
        start_time, num_days, coin = get_args()
    except:
        raise ValueError("Be sure to include start_time, num_days, and coin")

    output, filename = grab_data(start_time=start_time, num_days=num_days, coin=coin)
    write_data(filename=filename, array=output)

__main__()
