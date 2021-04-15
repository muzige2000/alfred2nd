from crawl import *
from stocks import *
import csv
import time
import os

date = time.strftime('%Y%m', time.localtime(time.time()))
codes = stock_codes()
output = f"results/data{date}.csv"


def contains(filename, code):
    if not os.path.isfile(filename):
        return False

    csv_file = csv.reader(open(filename, "r"), delimiter=",")
    for row in csv_file:
        if code == row[0]:
            return True
    return False


def append(filename, data):
    mode = "a" if os.path.isfile(filename) else "w"
    with open(filename, mode, encoding='utf-8-sig', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(list(data.values()))
        f.close()


count = 0
total = len(codes)

for idx, code in enumerate(codes):
    count += 1
    try:
        if contains(output, code):
            print(f'{count}/{total} ##### {code} pass')
            continue

        market = get_market(code)
        print(market)

        if market == 'KONEX':
            print(f'{count}/{total} ##### {code} pass KONEX')
            continue

        data, rowData = crawl(code)
        pp(data, width=30)
        pp(rowData, width=30)
        append(output, rowData)
        print(f'{count}/{total} ##### {code} done')
    except Exception as e:
        print(e)
        time.sleep(20)
    time.sleep(2)
