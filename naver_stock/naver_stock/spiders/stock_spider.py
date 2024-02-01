import sys
import scrapy
from scrapy import Spider
from scrapy import Request

sys.dont_write_bytecode = True # 캐시 비활성화

class StockSpider(Spider):
    name = "stock"
    start_url = "https://finance.naver.com/item/sise.naver?code=005930"
    url = "https://finance.naver.com"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
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
        day = self.url + response.xpath("//iframe[2]/@src").get()
        yield Request(
            url=day,
            headers=self.headers,
            callback=self.parse_stock
        )
        
    def parse_stock(self, response):
        for i in range(3, 16):
            if 8 <= i <= 10:
                continue
            
            # 날짜 확인
            date = response.xpath(f"//table[@class='type2']/tr[{i}]/td[1]/span[@class='tah p10 gray03']/text()").get()
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
            
            print(f"\ndate: {date}")
            print(f"end_price: {end_price}")
            print(f"change: {change}")
            print(f"start_price: {start_price}")
            print(f"high_price: {high_price}")
            print(f"low_price: {low_price}")
            print(f"volume: {volume}")
            