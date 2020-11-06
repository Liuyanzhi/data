import re
import time
import scrapy

from datetime import datetime
from scrapy.http import Request

pattern = re.compile('(\d+)')
price_pattern = re.compile('(\d+.\d+)')
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+08'
CN_FORMAT = '%A, %B %d, %Y %I:%M %p'
CN_ONE_FORMAT = '%Y年%m月%d日 %H:%M'

class WebSpider(scrapy.Spider):
	name = "webspider"
	start_urls = ["https://www.huodongxing.com/events?page=1"]
	headers = {"Host":"www.huodongxing.com","Connection":"keep-alive","Pragma":"no-cache","Cache-Control":"no-cache","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Sec-Fetch-Site":"none","Sec-Fetch-Mode":"navigate","Sec-Fetch-Dest":"document","Accept-Encoding":"gzip, deflate, br","Accept-Language":"zh-CN,zh;q=0.9"}
	cookie = {'Cookie': 'uid=e1b53578-f83d-4bd5-8bdb-69fba6d1ba77; route=1c148779685bf6c8f7fa768a9676bc01; ASP.NET_SessionId=egjahn2cy1cwnwf1njg0bsct; _ga=GA1.2.430962407.1604486451; _gid=GA1.2.541358790.1604486451; Hm_lvt_d89d7d47b4b1b8ff993b37eafb0b49bd=1604486451; HDX_REGION=%2c; Hm_lpvt_d89d7d47b4b1b8ff993b37eafb0b49bd=1604641535'}

	def _monkey_patching_HTTPClientParser_statusReceived(self):
		from twisted.web._newclient import HTTPClientParser, ParseError
		old_sr = HTTPClientParser.statusReceived
		def statusReceived(self, status):
			try:
				return old_sr(self, status)
			except ParseError as e:
				if e.args[0] == 'wrong number of parts':
					return old_sr(self, status + ' OK')
				raise
		statusReceived.__doc__ = old_sr.__doc__
		HTTPClientParser.statusReceived = statusReceived

	def start_requests(self):
		for url in self.start_urls:
			self._monkey_patching_HTTPClientParser_statusReceived()
			yield Request(url, headers=self.headers, cookies=self.cookie, callback=self.parse, dont_filter=True)

	def parse(self, response):
		for card in response.css('.search-tab-content-item-mesh'):
			href = card.css("div.search-tab-content-item-mesh a::attr(href)").extract_first()
			# print(href)
			time.sleep(10)
			yield Request(url="https://www.huodongxing.com" + href, headers=self.headers, cookies=self.cookie, callback=self.parse, dont_filter=True)
		if "https://www.huodongxing.com/events?page=" not in response.url:
			url = response.css("div.detail-link-div a::attr(href)").extract_first()
			match = pattern.search(url)
			title = response.css("p.detail-pp::text").get()
			time_text = response.css("div.address-info-wrap div::text").extract_first()
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
			address = response.css("div.address a::text").extract_first()
			if address is None :
				address = response.css("div.address span::text").extract_first()
			tickets = response.selector.re('"PriceStr":"[\u4E00-\u9FA50-9.¥]+"')
			prices = []
			for row in list(set(tickets)):
				if "免费" not in row:
					price = price_pattern.search(row)
					if price :
						prices.append(price.group())
			if len(prices) == 0 :
				prices.append('0')
			limit_text = response.css("div.address-info-wrap div::text").extract()[1]
			limit_match = pattern.search(limit_text.strip())
			limit_num = 0
			if limit_match :
			    limit_num = limit_match.group()
			baoming = response.css("div.func-baoming-wrap")
			follow = baoming.css(".num::text").extract_first()
			visitor = baoming.css("div.share .text-muted::text").extract_first()
			visitor_match = pattern.search(visitor)
			tags = response.css("div.tags.tags-list a::text").extract()
			media = response.css("div.media-body div:nth-child(4)")
			orgList = media.css("a.link-a-hover::attr(href)").extract()
			orgEs = []
			for row in orgList:
				org = row.replace("https://www.huodongxing.com", "").replace("http://", "").replace(".huodongxing.com", "")
				orgEs.append(org)
			# print("***************")
			# print("id", match.group())
			# print("链接",url)
			# print("名称",title)
			# print("开始时间",start)
			# print("结束时间",end)
			# print("地址",address)
			# print("价格",prices)
			# print("限量",limit_num)
			# print("收藏",follow)
			# print("浏览",visitor_match.group())
			# print("标签",tags)
			# print("机构",orgEs)
			# print("***************")
			with open('/root/spider/log.txt', 'a') as f:
				f.write('{{\"id\": \"{0}\", \"name\": \"{1}\", \"start_at\": \"{2}\", \"end_at\": \"{3}\", \"location\": \"{4}\", \"price\": \"{5}\", \"member_limit\": \"{6}\", \"follow\": \"{7}\", \"view\": \"{8}\", \"label\": \"{9}\", \"oids\": \"{10}\", \"url\": \"{11}\"}},\n'.format(
					match.group(), title, start, end, address, ','.join(prices), limit_num, follow, visitor_match.group(), ','.join(tags), ','.join(orgEs), url))
		# else:
		# 	pages = 1000
		# 	for i in range(2, pages):
		# 		time.sleep(300)
		# 		nextPage = "https://www.huodongxing.com/events?page=" + str(i)
		# 		# print(nextPage)
		# 		yield Request(url=nextPage, headers=self.headers, cookies=self.cookie, callback=self.parse, dont_filter=True)
