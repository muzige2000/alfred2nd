import pandas as pd
from selenium import webdriver
import selenium as se
import time
import json
import os


def get_market(code):
    cache = "results/market.json"
    markets = {}
    if os.path.isfile(cache):
        with open(cache, "r") as file:
            markets = json.load(file)

    if code in markets:
        return markets[code]

    url = f"https://m.stock.naver.com/item/main.nhn#/stocks/{code}/total"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    options = se.webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = se.webdriver.Chrome(chrome_options=options)
    driver.get(url)
    time.sleep(3)
    elem = driver.find_element_by_xpath('//*[@id="header"]/div[5]/div[1]/div/div[2]/div/div[1]/span/span')
    markets[code] = elem.text
    with open(cache, "w") as json_file:
        json.dump(markets, json_file)

    return markets[code]


def stock_codes():
    df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    codes = []
    new_count = 0
    for index, row in df.iterrows():
        print(row)
        code = '%06d' % int(row["종목코드"])
        # name = row["회사명"]
        # account_month = row["결산월"]
        codes.append(code)

    print("stocks: ", len(codes))
    return codes
