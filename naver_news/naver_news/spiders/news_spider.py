import scrapy 
from scrapy import Spider
from scrapy import Request

class NewsSpider(Spider):
    name = "news"
    start_url = "https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=001"
    url = "https://news.naver.com/main/list.naver"
    list_url = url + "{}"
    date_list = []
    page_list = []
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    def start_requests(self):
        """크롤러가 시작하면서 실행하는 메소드"""
        return [
            scrapy.Request(
                url=self.start_url,
                headers=self.headers,
                callback=self.parse_list
            )
        ]
        
    def parse_list(self, response):
        """뉴스 목록 확인"""
        
        pages = response.xpath("//div[@class='paging']/a/@href").getall()
        
        next_list = False
        
        for page in pages:
            next_list = True
            page = self.list_url.format(page)
            if page not in self.page_list:
                self.page_list.append(page)
        
        if next_list:
            last_page = self.page_list[-1]
            yield Request(
                url=self.list_url.format(last_page),
                headers=self.headers,
                callback=self.parse_list
            )
                
        for page in self.page_list:
            yield Request(
                url=page,
                headers=self.headers,
                callback=self.parse_news
            )
        
    def parse_news(self, response):
        print(f"url: {response.url}")