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

headers={'User-Agent':random.choice('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36')}

"""
{
   "id": "", // 主键 ID, varchar(255)
   "kind": "org", // 举办方类型, org | people
   "name": "FAYA TALK", // text
   "description": "一个聚焦社会议题的社区。",  // text
   "event_count": 16, // int
   "member": 30 // int
}
"""

keys = []

def send_request(url):
    """
    爬取一个页面
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    org_list = soup.find("ul", attrs=["class","organizer-lv2-list"])
    for card in org_list.children:
        second = random.randint(4,10)
        time.sleep(second)
        try:
            org_href = card.a.attrs["href"]
        except Exception as e:
            continue
        if "huodongxing.com" in org_href:
            org_id = org_href.replace("http://", "").replace(".huodongxing.com", "")
            org_url = org_href.replace("http://", "https://")
        else:
            org_id = org_href.split("/")[2]
            org_url = "https://www.huodongxing.com{0}".format(org_href)
        if org_id in keys:
            continue
        else:
            keys.append(org_id)
        sub_query = requests.get(org_url.strip())
        sub_soup = BeautifulSoup(sub_query.text,'html.parser')
        try:
            org_aside = sub_soup.find("div", attrs=["class", "org-aside-info"])
            spans = org_aside.find_all("span")
            event_count = spans[0].strong.text
            vip_count = spans[1].strong.text
            desc = org_aside.find("p").text
            org_avatar = sub_soup.find("div", attrs=["class", "org-avatar"])
            name = org_avatar.h2.text
            print("***************")
            print("id", org_id)
            print("name", name)
            print("description", desc)
            print("event_count", event_count)
            print("member", vip_count)
            print("***************")
            with open('/root/spider/org-log.txt', 'a') as f:
                f.write('{{\"id\": \"{0}\", \"name\": \"{1}\", \"description\": \"{2}\", \"event_count\": \"{3}\", \"member\": \"{4}\"}},\n'.format(
                    org_id, name.strip(), desc.strip(), event_count, vip_count))
        except Exception as e:
            print(e)
            with open('/root/spider/org-log.txt', 'a') as f:
                f.write('{{\"url\": \"{0}\"}},\n'.format(org_url))

if __name__ == "__main__":
    # send_request('https://www.huodongxing.com/zhubanfang/a?pi=1&tag=%e5%85%a8%e9%83%a8')
    pages = 4500
    for i in range(1, pages):
        send_request('https://www.huodongxing.com/zhubanfang/a?pi={0}&tag=%e5%85%a8%e9%83%a8'.format(i))
