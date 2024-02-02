import scrapy
from scrapy import Spider
from scrapy import Request
from datetime import datetime, timedelta
# from items import StockItem

class StockSpider(Spider):
    name = "stock"
    start_url = "https://finance.naver.com/item/sise.naver?code=005930"
    url = "https://finance.naver.com"
    list_url = url + "{}&page={}"
    url_list = []
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    def __init__(
        self,
        start_date = "2023-08-01",
        end_date = "2023-08-31",
    ):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        assert self.start_date.timestamp() <= self.end_date.timestamp(), "end_date이 start_date보다 앞에 있습니다."
    
    def start_requests(self):
        """크롤러가 시작하면서 실행하는 메소드"""
        return[
            scrapy.Request(
                url=self.start_url,
                headers=self.headers,
                callback=self.parse_iframe
            )
        ]
    
    def parse_iframe(self, response):
        """일별 시세 url 추출 후 이동"""
        global day
        day = response.xpath("//iframe[2]/@src").get()
        
        for page in range(1, 11):
            yield Request(
                url=self.list_url.format(day, str(page)),
                headers=self.headers,
                callback=self.parse_stock
            )
        
    def parse_stock(self, response):
    
        if response.url == self.list_url + day:
            page = 1
        else:
            page = (response.url).split("&")[1].split("=")[1]
        
        for i in range(3, 16):
            if 8 <= i <= 10:
                continue
            
            # 날짜 확인
            date = response.xpath(f"//table[@class='type2']/tr[{i}]/td[1]/span[@class='tah p10 gray03']/text()").get()
            date = datetime.strptime(date, "%Y.%m.%d")
            
            if self.start_date <= date <= self.end_date:
                next_list = True
                
                if response.url not in self.url_list:
                    self.url_list.append(response.url)
                
            elif self.end_date < date:
                next_list = True
            
        if next_list:
            next_page = int(page) + 10
            yield Request(
                url=self.list_url.format(day, str(next_page)),
                headers=self.headers,
                callback=self.parse_stock
            )
        else: 
            pass
            
        for url in self.url_list:
            print(f"url: {url}")