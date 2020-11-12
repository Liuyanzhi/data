import re
import json
import time
import random
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

pattern = re.compile('(\d+)')
price_pattern = re.compile('(\d+.\d+)')
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+08'
CN_FORMAT = '%A, %B %d, %Y %I:%M %p'
CN_ONE_FORMAT = '%Y年%m月%d日 %H:%M'
keys = []

headers = {
    'User-Agent':
        random.choice([
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)"',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; TencentTraveler 4.0; .NET CLR 2.0.50727)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; InfoPath.2; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; 360SE)',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; InfoPath.2; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER) ',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)'
        ])}


def get_price(body):
    price_str = re.search("eventTicketsJson.*?\];", body, re.M | re.I).group()
    price_str = price_str.replace("eventTicketsJson = ", "")
    return json.loads(price_str[:-1])


def get_avg_price(tickets):
    prices = []
    amount = 0
    for row in tickets:
        try:
            row_text = row['PriceStr']
            if "免费" not in row_text:
                price = price_pattern.search(row_text)
                if price:
                    ticket = price.group().replace(",", "")
                    prices.append(ticket)
                    try:
                        amount += float(ticket)
                    except Exception as e:
                        print(e)
                        print(ticket)
        except Exception as e:
            print(e)
            print(tickets)
            continue
    if amount != 0:
        amount = '%.2f' % (amount/len(prices))
    return amount


def format_date(time_text):
    result = "2020-00-00 00:00:00"
    try:
        result = datetime.strptime(time_text, GMT_FORMAT)
    except Exception as e:
        try:
            result = datetime.strptime(time_text, CN_FORMAT)
        except Exception as e:
            try:
                result = datetime.strptime(time_text, CN_ONE_FORMAT)
            except Exception as e:
                print(time_text)
                print(e)
    return result


def get_event_id(event_url):
    try:
        match_url = pattern.search(event_url)
        event_id = match_url.group()
    except Exception as e:
        print(event_url)
        print(e)
        event_id = event_url.split("/")[-1]
    return event_id


def first_page(sub_query, sub_soup, file_name):
    event_url = sub_soup.find("div", attrs=["class", "detail-link-div"]).a.attrs["href"]
    event_id = get_event_id(event_url)
    title = sub_soup.find("p", attrs=["class", "detail-pp"]).text
    time_text = sub_soup.find("div", attrs=["class", "address-info-wrap"]).div.text
    time_split = time_text.strip().split("～")
    start = format_date(time_split[0].strip())
    end = format_date(time_split[1].strip())
    try:
        address = sub_soup.find("div", attrs=["class", "address"]).a.text
    except Exception as e:
        address = sub_soup.find("div", attrs=["class", "address"]).span.text
    tickets = get_price(sub_query.text)
    price = get_avg_price(tickets)
    limit_text = sub_soup.find("div", attrs=["class", "address-info-wrap"]).find_all("div")[1].text
    limit_match = pattern.search(limit_text.strip())
    limit_num = 0
    if limit_match:
        limit_num = limit_match.group()
    baoming = sub_soup.find("div", attrs=["class", "func-baoming-wrap"])
    follow = baoming.find("span", attrs=["class", "num"]).text
    visitor = baoming.find("div", attrs=["class", "share"]).find("span",
                                                                 attrs=["class", "text-muted"]).text
    visitor_num = pattern.search(visitor).group()
    try:
        tag = sub_soup.find("div", attrs=["class", "tags tags-list"]).a.text
    except Exception as e:
        tag = ""
    try:
        org_href = \
        sub_soup.find("div", attrs=["class", "jumbotron media"]).find("div", attrs=["class", "media-body"]).find(
            "div", title="活动发起人").a.attrs["href"]
        org_id = org_href.replace("https://www.huodongxing.com", "").replace("http://", "").replace(
            ".huodongxing.com", "")
    except Exception as e:
        org_id = "无"
    with open(file_name, 'a') as f:
        f.write(
            '{{\"id\": \"{0}\", \"name\": \"{1}\", \"start_at\": \"{2}\", \"end_at\": \"{3}\", \"location\": \"{4}\", \"price\": \"{5}\", \"member_limit\": \"{6}\", \"follow\": \"{7}\", \"view\": \"{8}\", \"label\": \"{9}\", \"oids\": \"{10}\", \"url\": \"{11}\"}},\n'.format(
                event_id, title, start, end, address, price, limit_num, follow, visitor_num,
                tag,
                org_id, event_url))


def second_page(sub_url, sub_soup, sub_query, file_name):
    event_id = get_event_id(sub_url)
    title = sub_soup.find("div", attrs=["class", "event-intro"]).h2.text
    time_text = sub_soup.find("div", attrs=["class", "event-details-lite-meta-left"]).text
    address = sub_soup.find("div", attrs=["class", "set-address-width"]).text
    time_split = time_text.replace(address, "").strip().split("～")
    start = format_date(time_split[0].strip())
    end = format_date(time_split[1].strip())
    tickets = get_price(sub_query.text)
    price = get_avg_price(tickets)
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
                event_id, title, start, end, address, price, limit_num, follow, visitor_num,
                tag,
                org_id, sub_url))


def send_request(link, file_name):
    """
    爬取一个页面
    """
    pages = 100
    for i in range(1, pages):
        link_url = link+str(i)
        response = requests.get(link_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all("div", attrs=["class", "search-tab-content-item-mesh"])
        if len(cards) == 0:
            second = random.randint(60, 300)
            time.sleep(second)
            print(link_url)
            break
        for card in cards:
            sub_href = card.a.attrs["href"]
            sub_href = sub_href.split("?")[0].lower()
            if sub_href in keys:
                continue
            else:
                keys.append(sub_href)
            sub_url = "https://www.huodongxing.com" + sub_href
            second = random.randint(5, 10)
            time.sleep(second)
            sub_query = requests.get(sub_url, headers=headers)
            if sub_query.status_code == 404 or sub_query.url == 'https://www.huodongxing.com/':
                pass
            else:
                sub_soup = BeautifulSoup(sub_query.text, 'html.parser')
                if sub_soup is None:
                    print(sub_url)
                    continue
                try:
                    first_page(sub_query, sub_soup, file_name)
                except Exception as e:
                    try:
                        second_page(sub_url, sub_soup, sub_query, file_name)
                    except Exception as e:
                        print(e)
                        with open(file_name, 'a') as f:
                            f.write('{{\"url\": \"{0}\"}},\n'.format(sub_url))


if __name__ == "__main__":
    begin_date = datetime.strptime("2019-03-01", '%Y-%m-%d')
    end_date = datetime.strptime("2019-03-30", '%Y-%m-%d')
    now = begin_date
    url = "https://www.huodongxing.com/events?orderby=n&d=ts&date={0}&dateTo={1}&city=%E5%85%A8%E9%83%A8&page="
    while begin_date <= end_date:
        begin_date += timedelta(days=1)
        start = now.strftime('%Y-%m-%d')
        end = begin_date.strftime('%Y-%m-%d')
        send_request(url.format(start, end), "{0}.txt".format(start))
        now = begin_date
