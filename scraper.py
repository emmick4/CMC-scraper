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
    url = "https://graphs2.coinmarketcap.com/currencies/{coin}/{ts}/{ts2}/".format(ts=ts, ts2=ts+step, coin=coin)
    print(url)
    response = call_api(url)
    return response

def parse_output(output, coin):
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
        d = {"ts": str(ts), "price_usd": str(price_usd), "price_btc": str(price_btc), "volume": str(volume), "mcap": str(mcap), "coin":coin}
        ts_table.append(d)
    return ts_table

def ts_to_str(ts):
    struct_time = time.gmtime(ts)
    return time.strftime("%m-%d-%Y %H:%M", struct_time)

def name_file(start_time, num_days, coin):
    end_timestamp = start_time + (num_days * 86400)
    start_str = ts_to_str(start_time)
    end_str = ts_to_str(end_timestamp)
    filename = "pricing - " + coin + ".csv"# + " " + start_str + ' - ' + end_str + ".csv"
    return filename

def estimate_time_left(start_time, pct_left):
    now = time.time()
    seconds_spent = now - start_time
    return seconds_spent * (pct_left/ (1 - pct_left))

def status_update(count, num_days, started_at):
    print(
        "Scraping Day", "{on}/{total}".format(on=count, total=int(num_days//1)), "|",
        str(round((count / num_days) * 100, 2)) + "%", "|",
        "{}s left".format(round(estimate_time_left(started_at, 1 - count/num_days)))
        )

def grab_data(start_time, num_days, coin):
    print("Grabbing data")
    times = [start_time + (i * 86400) for i in range(int(num_days // 1))]
    complete_array = []
    count = 1
    started = time.time()
    OG_in = False
    from multiprocessing import Queue, Process
    import queue
    scrape_queue = Queue()
    parse_queue = Queue()
    done_queue = Queue()
    num_processes= 7
    for i in range(num_processes):
        Process(target=worker, args=(scrape_queue, parse_queue)).start()
    Process(target=worker, args=(parse_queue, done_queue)).start()

    for ts in times:
        scrape_queue.put((scrape, [coin, ts]))
    count = 0
    print("scrape queue filled")
    flag, fail_count = True, 0
    while flag:
        print("scraped {}/{}".format(count, len(times)))
        try:
            output = parse_queue.get_nowait()
            complete_array.extend(parse_output(output, coin))
            count += 1
            fail_count = 0
        except queue.Empty:
            fail_count += 1
            time.sleep(0.5)
            if fail_count > 20:
                flag = False
    # count = 0
    # print("scrape queue cleared")
    # parse_queue_flag = True
    # empty_count = 0
    # while parse_queue_flag:
    #     print("parsed {}/{}".format(count, len(times)))
    #     count += 1
    #     try:
    #         parsed = done_queue.get_nowait()
    #         complete_array.extend(parsed)
    #     except queue.Empty:
    #         empty_count += 1
    #         time.sleep(0.25)
    #         if empty_count > 25:
    #             parse_queue_flag = False
    print("finished parsing")

    if OG_in == False and complete_array != []:
        OG_in = True
        d = {"ts": 1,
        "price_usd": complete_array[0]['price_usd'],
        "price_btc": complete_array[0]['price_btc'],
        "volume": complete_array[0]['volume'],
        "mcap": complete_array[0]['mcap'],
        "coin": coin
        }
        complete_array.append(d)
    for i in range(num_processes):
        scrape_queue.put("STOP")
    parse_queue.put("STOP")
    print("data scraped")
    print(len(complete_array), "rows of data")

    return complete_array, name_file(start_time, num_days, coin)

def write_data(filename, array):
    with open(filename, "w+") as csvfile:
        field_names = ["ts", "price_usd", "price_btc", "volume", "mcap", "coin"]
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
            coin = arg.replace("coin=", "")
    try:
        num_days
    except NameError:
        num_days = (time.time() - start_time)/86400
    return start_time, num_days, coin

def __main__():
    try:
        start_time, num_days, coin = get_args()
    except:
        raise ValueError("Be sure to include start_time, num_days, and coin")

    output, filename = grab_data(start_time=start_time, num_days=num_days, coin=coin)
    print("writing data")
    write_data(filename=filename, array=output)

def grab_24h_data(ts, coin):
    output = scrape(coin, ts)
    print(output)
    return parse_output(output)

def worker(input, output):
    for func, args in iter(input.get, 'STOP'):
        result = job(func, args)
        output.put(result)
def job(func, args):
    result = func(*args)
    return result

# print(grab_24h_data(ts=1519661845, coin="bitcoin"))
if __name__ == "__main__":
    __main__()
