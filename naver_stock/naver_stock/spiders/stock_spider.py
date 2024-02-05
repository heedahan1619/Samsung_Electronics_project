import scrapy
from scrapy import Spider
from scrapy import Request
from datetime import datetime, timedelta
from naver_stock.items import NaverStockItem

class StockSpider(Spider):
    name = "stock"
    start_url = "https://finance.naver.com/item/sise.naver?code=005930"
    url = "https://finance.naver.com"
    list_url = url + "{}&page={}"
    url_list = []
    items = []
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
            
        next_list = False
        
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
                    
                # for i in range(3, 16):
                #     if 8 <= i <= 10:
                #         continue

                date = response.xpath(f"//table[@class='type2']/tr[{i}]/td[1]/span[@class='tah p10 gray03']/text()").get()
                date = datetime.strptime(date, "%Y.%m.%d")
                end_price = response.xpath(f"//table[@class='type2']/tr[{i}]/td[2]/span[@class='tah p11']/text()").get()
                class_name = response.xpath(f"//table[@class='type2']/tr[{i}]/td[3]/span[contains(@class, 'tah p11') or contains(@class, 'tah p11 nv01') or contains(@class, 'tah pa11 red02')]/@class").get()
                if "nv01" in class_name:
                    prefix = "하락"
                elif "red02" in class_name:
                    prefix = "상승"
                else:
                    prefix = ""
                value = response.xpath(f"//table[@class='type2']/tr[{i}]/td[3]/span[contains(@class, 'tah p11') or contains(@class, 'tah p11 nv01') or contains(@class, 'tah pa11 red02')]/text()").get().strip()
                change = f"{prefix} {value}"
                start_price = response.xpath(f"//table[@class='type2']/tr[{i}]/td[4]/span[@class='tah p11']/text()").get()
                high_price = response.xpath(f"//table[@class='type2']/tr[{i}]/td[5]/span[@class='tah p11']/text()").get()
                low_price = response.xpath(f"//table[@class='type2']/tr[{i}]/td[6]/span[@class='tah p11']/text()").get()
                volume = response.xpath(f"//table[@class='type2']/tr[{i}]/td[7]/span[@class='tah p11']/text()").get()

                stock_item = {
                "date": date,
                "end_price": end_price,
                "change": change,
                "start_price": start_price,
                "high_price": high_price,
                "low_price": low_price,
                "volume": volume
                }

                if self.start_date <= date <= self.end_date:
                    item = NaverStockItem()
                    item["date"] = stock_item["date"]
                    item["end_price"] = stock_item["end_price"]
                    item["change"] = stock_item["change"]
                    item["start_price"] = stock_item["start_price"]
                    item["high_price"] = stock_item["high_price"]
                    item["low_price"] = stock_item["low_price"]
                    item["volume"] = stock_item["volume"]
                    
                    print(f"\ndate: {item['date']}")
                    print(f"end_price: {item['end_price']}")
                    print(f"change: {item['change']}")
                    print(f"start_price: {item['start_price']}")   
                    print(f"high_price: {item['high_price']}")
                    print(f"low_price: {item['low_price']}")
                    print(f"volume: {item['volume']}")

            elif self.end_date < date:
                next_list = True
        
        if next_list:
            next_page = int(page) + 10
            yield Request(
                url=self.list_url.format(day, str(next_page)),
                headers=self.headers,
                callback=self.parse_stock
            )
            
        
            