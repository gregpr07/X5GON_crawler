from bs4 import BeautifulSoup
import scrapy
from datetime import datetime
import re
import logging


class X5Spider(scrapy.Spider):
    name = "vidraSI"

    page = ''
    baseurl = 'http://vidra.si/index.html'
    provider = 'vidra.si'

    start_urls = [
        baseurl
    ]
    dateYMD = str(datetime.now().strftime("%Y-%m-%d"))

    def parse(self, response):
        to_visit = response.css('.toc a::attr(href)').getall()

        for ucbenik in to_visit:
            yield response.follow(ucbenik, callback=self.parsePage)

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

    def parsePage(self, response):

        yield {
            'title': title,
            'path': path,
            'provider_uri': providerurl,
            'provider': self.provider,
            'material_url': url,
            'description': text_left+text_right,
            'tasks': tasks,
            'resources': {'imgs': absimgs, 'videos': absvideos, 'audios': absaudios},
            'language': 'sl',
            'type': {"ext": "html", "mime": "text/html"},
            'date_retrieved': self.dateYMD,
            'license': licenca,
        }
        next_page = response.css('.paging-right a::attr(href)').get()
