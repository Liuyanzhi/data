import re
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


def send_request(url, file_name):
    """
    爬取一个页面
    """
    try:
        sub_query = requests.get(url)
        sub_soup = BeautifulSoup(sub_query.text, 'html.parser')
        try:
            event_url = sub_soup.find("div", attrs=["class", "detail-link-div"]).a.attrs["href"]
            match_url = pattern.search(event_url)
            event_id = match_url.group()
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
            tickets = sub_soup.find_all(re.compile('"PriceStr":"[\u4E00-\u9FA50-9.¥]+"'))
            prices = []
            for row in list(set(tickets)):
                if "免费" not in row:
                    price = price_pattern.search(row)
                    if price:
                        prices.append(price.group())
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
            tag = sub_soup.find("div", attrs=["class", "tags tags-list"]).a.text
            org_href = \
                sub_soup.find("div", attrs=["class", "jumbotron media"]).find("div", attrs=["class", "media-body"]).find(
                    "div", title="活动发起人").a.attrs["href"]
            org_id = org_href.replace("https://www.huodongxing.com", "").replace("http://", "").replace(
                ".huodongxing.com", "")
            with open(file_name, 'a') as f:
                f.write(
                    '{{\"id\": \"{0}\", \"name\": \"{1}\", \"start_at\": \"{2}\", \"end_at\": \"{3}\", \"location\": \"{4}\", \"price\": \"{5}\", \"member_limit\": \"{6}\", \"follow\": \"{7}\", \"view\": \"{8}\", \"label\": \"{9}\", \"oids\": \"{10}\", \"url\": \"{11}\"}},\n'.format(
                        event_id, title, start, end, address, ','.join(prices), limit_num, follow, visitor_num, tag,
                        org_id, event_url))
        except Exception as e:
            match_url = pattern.search(url)
            event_id = match_url.group()
            title = sub_soup.find("div", attrs=["class", "event-intro"]).h2.text
            time_text = sub_soup.find("div", attrs=["class", "event-details-lite-meta-left"]).text
            address = sub_soup.find("div", attrs = ["class", "set-address-width"]).text
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
            tickets = sub_soup.find_all(re.compile('"PriceStr":"[\u4E00-\u9FA50-9.¥]+"'))
            prices = []
            for row in list(set(tickets)):
                if "免费" not in row:
                    price = price_pattern.search(row)
                    if price:
                        prices.append(price.group())
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
            org_href = sub_soup.find("div", attrs=["class", "event-details-lite-org-div"]).a.attrs["href"]
            org_id = org_href.replace("https://www.huodongxing.com", "").replace("http://", "").replace(
                ".huodongxing.com", "")
            with open(file_name, 'a') as f:
                f.write(
                    '{{\"id\": \"{0}\", \"name\": \"{1}\", \"start_at\": \"{2}\", \"end_at\": \"{3}\", \"location\": \"{4}\", \"price\": \"{5}\", \"member_limit\": \"{6}\", \"follow\": \"{7}\", \"view\": \"{8}\", \"label\": \"{9}\", \"oids\": \"{10}\", \"url\": \"{11}\"}},\n'.format(
                        event_id, title, start, end, address, ','.join(prices), limit_num, follow, visitor_num, tag,
                        org_id, url))
    except Exception as e:
        print(url)
        with open(file_name, 'a') as f:
            f.write('{{\"url\": \"{0}\"}},\n'.format(url))


if __name__ == "__main__":
    data = ["https://www.huodongxing.com/go/gjs"]
    for row in data:
        try:
            second = random.randint(5, 10)
            time.sleep(second)
            send_request(row, "huodong_recover.log")
        except Exception as e:
            print(row)
            second = random.randint(300, 600)
            time.sleep(second)
