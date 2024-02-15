import re
import json
import requests
import scrapy 
from scrapy import Spider
from scrapy import Request
from datetime import datetime
from naver_news.items import NaverNewsItem

# 정규표현식 불러와서 적용
import naver_news.constants as reg

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
        """뉴스 기사 url 추출"""
        for li in response.xpath("//ul[@class='type06_headline']/li"):
            url = li.xpath("dl/dt/a/@href").get()
            yield Request(
                url=url,
                headers=self.headers,
                callback=self.parse_news_item
            )
            
    def parse_news_item(self, response):
        """뉴스 기사 항목 추출"""
            
        print(f"\nurl: {response.url}")
        
        item = NaverNewsItem()
        
        #일반 및 스포츠 기사
        if "news" in response.url:
            date = response.xpath("//span[@class='media_end_head_info_datestamp_time _ARTICLE_DATE_TIME']/text() | //div[@class='info']/span/text()").get()
            if "기사입력" in date:
                date = date[5:]
            if "sports" in response.url:
                item["category"] = "스포츠"
            else:
                item["category"] = item["category"] = response.xpath("//em[@class='media_end_categorize_item']/text()").get()
            item["title"] = response.xpath("//h2[@id='title_area']/span/text() | //h4[@class='title']/text()").get().strip().replace("\n", "")    
            item["content"] = " ".join(response.xpath("//article[@id='dic_area']/strong/text() | //div[@id='newsEndContents']/strong/text() | //div[@id='newsEndContents']/text() | //article[@id='dic_area']/text()").getall()).strip().replace("\n", "")
        
        # 연예 기사
        else:
            date = response.xpath("//div[@class='article_info']/span/em/text()").get()
            
            item["category"] = "연예"
            
            item["title"] = response.xpath("//h2[@class='end_tit']/text()").get().strip()
            
            item["content"] = " ".join(response.xpath("//div[@id='articeBody']/text()").getall()).strip().replace("\n", "")
        
        #시간 전처리
        if "오전" in date:
            date = date.split("오전")[0] + " " + date.split("오전")[1]
        else:
            if date[-5:].split(":")[0] != "12":
                time = int(date[-5:].split(":")[0])+12
                time = str(time) + ":" + date[-5:].split(":")[1]
                date = date.split(" ")[0] + " " + time
            else:
                date = date.split(" ")[0] + " " + date.split(" ")[2]
        if len(date.split(" ")[1].split(":")[0]) == 1:
            date = date.split(" ")[0] + " 0" + date.split(" ")[1].split(":")[0] + date[-3:]
            
        item["date"] = datetime.strptime(date, "%Y.%m.%d. %H:%M")
        
        #2개 이상인 공백을 공백으로 대체
        item["content"] = re.sub(r"\s{2,}", " ", item["content"]) 
        #정규표현식 적용
        regex = re.compile("|".join(reg.REGEX_PATTERN["연합뉴스"]))
        item["content"] = re.sub(regex, "", item["content"])
        
        reaction_dict = {}
        for a in response.xpath("//div[@class='_reactionModule u_likeit']/ul/li/a"):
            name = a.xpath("span[@class='u_likeit_list_name _label']/text()").get()
            count = a.xpath("span[@class='u_likeit_list_count _count']/text()").get()
            reaction_dict[name] = count
        item["reaction"] = reaction_dict
        
        #BeautifulSoup으로 json파일로 구성된 기사 반응 추출
        update = {}
        
        if "aid" in response.url:
            news_id = response.url.split("=")[-1]
        else:
            news_id = response.url.split("/")[-1]

        if "sports" in response.url:
            reaction_url = f"https://sports.like.naver.com/v1/search/contents?q=SPORTS%5Bne_001_{news_id}%5D"
        else:
            reaction_url = f"https://news.like.naver.com/v1/search/contents?q=NEWS%5Bne_001_{news_id}%5D"
        
        res = requests.get(reaction_url, headers=self.headers)
        reactions = res.json()["contents"][0]["reactions"]
        label = res.json()["contents"][0]["reactionTextMap"]["ko"]
        
        for reaction in reactions:
            type = reaction["reactionType"]
            count = reaction["count"]
            name = label[type]
            update[name] = count
        
        #데이터 업데이트
        for key in update:
            if key in reaction_dict:
                reaction_dict[key] = update[key]
            
        # print(f"date: {item['date']}")    
        # print(f"category: {item['category']}")
        # print(f"title: {item['title']}")
        # print(f"content: {item['content']}")
        print(f"reaction: {item['reaction']}")
        