from bs4 import BeautifulSoup
import scrapy
from datetime import datetime
import re


class X5Spider(scrapy.Spider):
    name = "cbcampus_spider"

    page = 0
    total_results = 28

    baseurl = f'https://open.bccampus.ca/browse-our-collection/find-open-textbooks/?start={page}&subject=&contributor=&searchTerm=&keyword='

    provider = 'open.bccampus.ca'

    start_urls = [
        f'{baseurl}',
    ]
    dateYMD = str(datetime.now().year)+"-" + \
        str(datetime.now().month)+"-"+str(datetime.now().day)

    def parse(self, response):
        to_visit = response.css(
            'ul.list-group li.list-group-item h4 a::attr(href)').getall()

        for i in range(1, self.total_results+1):
            self.page = i*10
            yield response.follow(f'?start={self.page}&subject=&contributor=&searchTerm=&keyword=', callback=self.parse)

        # ALL BOOKS
        for pagez in to_visit:
            yield response.follow(pagez, callback=self.parsePage)
        # SINGLE ITEM
        # yield response.follow(to_visit[0], callback=self.gifClick)

    def GetText(self, source):
        try:
            soup = BeautifulSoup(source)
            for script in soup(["script", "style", "video", "button", "input"]):
                script.decompose()
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip()
                      for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return(text)
        except:
            return('')

    def getTitle(self, path):
        try:
            return (re.findall("\|\s((\w)+(\s\w+)*)", path)[1][0])
        except:
            return (path)

    def parsePage(self, response):

        title = response.css('h2[itemprop="name"]::text').get()

        url = response.url
        providerurl = response.urljoin('../')
        licenca = response.css('.license-attribution a::attr(href)').get()

        yield {
            'title': title,
            'material_url': url,
            'date_retrieved': self.dateYMD,
            'license': licenca,
        }


'''
IDEAS:

response.css('.toc__part.toc__part--full ol p.toc__title a::attr(href)').getall() -> USA POGLAVJA


imgs = response.css('.container img::attr(src)').getall()
videos = response.css('.container video::attr(src)').getall()
audios = response.css('.container audio::attr(src)').getall()
absimgs = [response.urljoin(x) for x in imgs]
absvideos = [response.urljoin(x) for x in videos]
absaudios = [response.urljoin(x) for x in audios]


'''
