import re
import json
import time
import random
import requests

from bs4 import BeautifulSoup
from datetime import datetime

pattern = re.compile('(\d+)')
price_pattern = re.compile('(\d+.\d+)')
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+08'
CN_FORMAT = '%A, %B %d, %Y %I:%M %p'
CN_ONE_FORMAT = '%Y年%m月%d日 %H:%M'
keys = []
headers = {'User-Agent': random.choice(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36')}


def get_price(body):
    price_str = re.search("eventTicketsJson.*?\];", body, re.M|re.I).group()
    price_str = price_str.replace("eventTicketsJson = ", "")
    return json.loads(price_str[:-1])


def send_request(url, file_name):
    """
    爬取一个页面
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for card in soup.find_all("div", attrs=["class", "search-tab-content-item-mesh"]):
        sub_href = card.a.attrs["href"]
        sub_href = sub_href.split("?")[0].lower()
        if sub_href in keys:
            continue
        else:
            keys.append(sub_href)
        sub_url = "https://www.huodongxing.com" + sub_href
        try:
            second = random.randint(5, 10)
            time.sleep(second)
            sub_query = requests.get(sub_url)
            if sub_query.status_code == 404 or sub_query.url == 'https://www.huodongxing.com/':
                pass
            else:
                sub_soup = BeautifulSoup(sub_query.text, 'html.parser')
                try:
                    event_url = sub_soup.find("div", attrs=["class", "detail-link-div"]).a.attrs["href"]
                    try:
                        match_url = pattern.search(event_url)
                        event_id = match_url.group()
                    except Exception as e:
                        event_id = 'https://www.huodongxing.com/go/gjs'.split("/")[-1]
                    title = sub_soup.find("p", attrs=["class", "detail-pp"]).text
                    time_text = sub_soup.find("div", attrs=["class", "address-info-wrap"]).div.text
                    time_split = time_text.strip().split("～")
                    try:
                        start = datetime.strptime(time_split[0].strip(), GMT_FORMAT)
                    except Exception as e:
                        try:
                            start = datetime.strptime(time_split[0].strip(), CN_FORMAT)
                        except Exception as e:
                            start = datetime.strptime(time_split[0].strip(), CN_ONE_FORMAT)
                    try:
                        end = datetime.strptime(time_split[1].strip(), GMT_FORMAT)
                    except Exception as e:
                        try:
                            end = datetime.strptime(time_split[1].strip(), CN_FORMAT)
                        except Exception as e:
                            end = datetime.strptime(time_split[1].strip(), CN_ONE_FORMAT)
                    try:
                        address = sub_soup.find("div", attrs=["class", "address"]).a.text
                    except Exception as e:
                        address = sub_soup.find("div", attrs=["class", "address"]).span.text
                    prices = []
                    tickets = get_price(sub_query.text)
                    for row in tickets:
                        try:
                            row_text = row['PriceStr']
                            if "免费" not in row_text:
                                price = price_pattern.search(row_text)
                                if price:
                                    prices.append(price.group())
                        except Exception as e:
                            continue
                    if len(prices) == 0:
                        prices.append('0')
                    limit_text = sub_soup.find("div", attrs=["class", "address-info-wrap"]).find_all("div")[1].text
                    limit_match = pattern.search(limit_text.strip())
                    limit_num = 0
                    if limit_match:
                        limit_num = limit_match.group()
                    baoming = sub_soup.find("div", attrs=["class", "func-baoming-wrap"])
                    follow = baoming.find("span", attrs=["class", "num"]).text
                    visitor = baoming.find("div", attrs=["class", "share"]).find("span", attrs=["class", "text-muted"]).text
                    visitor_num = pattern.search(visitor).group()
                    try:
                        tag = sub_soup.find("div", attrs=["class", "tags tags-list"]).a.text
                    except Exception as e:
                        tag = ""
                    try:
                        org_href = sub_soup.find("div", attrs=["class", "jumbotron media"]).find("div", attrs=["class",
                                                                                                               "media-body"]).find(
                            "div", title="活动发起人").a.attrs["href"]
                        org_id = org_href.replace("https://www.huodongxing.com", "").replace("http://", "").replace(
                            ".huodongxing.com", "")
                    except Exception as e:
                        org_id = "无"
                    with open(file_name, 'a') as f:
                        f.write(
                            '{{\"id\": \"{0}\", \"name\": \"{1}\", \"start_at\": \"{2}\", \"end_at\": \"{3}\", \"location\": \"{4}\", \"price\": \"{5}\", \"member_limit\": \"{6}\", \"follow\": \"{7}\", \"view\": \"{8}\", \"label\": \"{9}\", \"oids\": \"{10}\", \"url\": \"{11}\"}},\n'.format(
                                event_id, title, start, end, address, ','.join(prices), limit_num, follow, visitor_num, tag,
                                org_id, event_url))
                except Exception as e:
                    try:
                        match_url = pattern.search(url)
                        event_id = match_url.group()
                    except:
                        event_id = 'https://www.huodongxing.com/go/gjs'.split("/")[-1]
                    title = sub_soup.find("div", attrs=["class", "event-intro"]).h2.text
                    time_text = sub_soup.find("div", attrs=["class", "event-details-lite-meta-left"]).text
                    address = sub_soup.find("div", attrs=["class", "set-address-width"]).text
                    time_split = time_text.replace(address, "").strip().split("～")
                    try:
                        start = datetime.strptime(time_split[0].strip(), GMT_FORMAT)
                    except Exception as e:
                        try:
                            start = datetime.strptime(time_split[0].strip(), CN_FORMAT)
                        except Exception as e:
                            start = datetime.strptime(time_split[0].strip(), CN_ONE_FORMAT)
                    try:
                        end = datetime.strptime(time_split[1].strip(), GMT_FORMAT)
                    except Exception as e:
                        try:
                            end = datetime.strptime(time_split[1].strip(), CN_FORMAT)
                        except Exception as e:
                            end = datetime.strptime(time_split[1].strip(), CN_ONE_FORMAT)
                    prices = []
                    tickets = get_price(sub_query.text)
                    for row in tickets:
                        try:
                            row_text = row['PriceStr']
                            if "免费" not in row_text:
                                price = price_pattern.search(row_text)
                                if price:
                                    prices.append(price.group())
                        except Exception as e:
                            continue
                    if len(prices) == 0:
                        prices.append('0')
                    limits = sub_soup.find_all(re.compile('"Quantity":[\u4E00-\u9FA50-9.¥]+'))
                    limit_num = 0
                    for row in list(set(limits)):
                        if row.isdigit():
                            limit_num += row
                    follow = sub_soup.find("a", attrs=["class", "event_like_icon"]).text
                    follow = follow.replace("收藏", "").strip()
                    visitor_num = 0
                    tag = ""
                    try:
                        org_href = sub_soup.find("div", attrs=["class", "event-details-lite-org-div"]).a.attrs["href"]
                        org_id = org_href.replace("https://www.huodongxing.com", "").replace("http://", "").replace(
                            ".huodongxing.com", "")
                    except Exception as e:
                        org_id = "无"
                    with open(file_name, 'a') as f:
                        f.write(
                            '{{\"id\": \"{0}\", \"name\": \"{1}\", \"start_at\": \"{2}\", \"end_at\": \"{3}\", \"location\": \"{4}\", \"price\": \"{5}\", \"member_limit\": \"{6}\", \"follow\": \"{7}\", \"view\": \"{8}\", \"label\": \"{9}\", \"oids\": \"{10}\", \"url\": \"{11}\"}},\n'.format(
                                event_id, title, start, end, address, ','.join(prices), limit_num, follow, visitor_num, tag,
                                org_id, url))
        except Exception as e:
            print(sub_url)
            with open(file_name, 'a') as f:
                f.write('{{\"url\": \"{0}\"}},\n'.format(sub_url))


if __name__ == "__main__":
    data = {"2019-01-01": "2019-01-30", "2019-02-01": "2019-02-28", "2019-03-01": "2019-03-30",
            "2019-04-01": "2019-04-30", "2019-05-01": "2019-05-30", "2019-06-01": "2019-06-30",
            "2019-07-01": "2019-07-30", "2019-08-01": "2019-08-30", "2019-09-01": "2019-09-30",
            "2019-10-01": "2019-10-30", "2019-11-01": "2019-11-30", "2019-12-01": "2019-12-30"}
    for k, v in data.items():
        file_name = "/root/spider/{0}.txt".format(k)
        pages = 1000
        for i in range(1, pages):
            try:
                send_request(
                    'https://www.huodongxing.com/events?orderby=n&d=ts&date={0}&dateTo={1}&city=%E5%85%A8%E9%83%A8&page={2}'.format(
                        k, v, i), file_name)
            except Exception as e:
                print(
                    'https://www.huodongxing.com/events?orderby=n&d=ts&date={0}&dateTo={1}&city=%E5%85%A8%E9%83%A8&page={2}'.format(
                        k, v, i))
                second = random.randint(300, 600)
                time.sleep(second)
