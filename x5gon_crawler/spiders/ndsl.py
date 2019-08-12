from bs4 import BeautifulSoup
import scrapy
from scrapy import Selector
from datetime import datetime
import re
import logging


class X5Spider(scrapy.Spider):
    name = "ndsl_spider"

    baseurl = 'https://nsdl.oercommons.org/browse?batch_size=100&batch_start='

    providerurl = f'https://nsdl.oercommons.org'

    provider = 'engageny.org'

    emptylicence = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'

    start_urls = [
        baseurl
    ]

    dateYMD = str(datetime.now().strftime("%Y-%m-%d"))

    def GetText(self, source):
        try:
            soup = BeautifulSoup(source, "lxml")
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

    def convert(self, date_time):
        formats = "%m/%d/%Y"  # The format
        time_date = datetime.strptime(date_time, formats)
        return time_date.strftime("%Y-%m-%d")

    def parse(self, response):
        num_loop = int(
            int(response.css('.items-number::text').get().strip('()'))/100+1)
        for i in range(num_loop):
            yield response.follow(self.baseurl+str(i*100), callback=self.parseBatch)

    def parseBatch(self, response):
        to_visit = response.css('.item-title a::attr(href)').getall()
        for page in to_visit:
            yield response.follow(page, callback=self.parsePage)

    def parsePage(self, response):

        title = response.css(
            '.material-title > a:nth-child(1)::text').get()
        material_url = response.css('#goto::attr(href)').get()

        description = response.css('dd.text p::text').get()

        url = response.url

        date = self.convert(response.css(
            '.materials-details-first-part dd.text::text').get())

        mime = response.css('dd span[itemprop=genre]::text').get()

        language = response.css(
            '.material-details-second-part span::attr(content)').get()
        licenca = response.css(
            '.material-details-second-part dd a[rel=license]::attr(href)').get()

        if not licenca:
            licenca = self.emptylicence

        yield {
            'title': title,
            'description': description,
            'material_uri': url,
            'material_url': material_url,
            'language': language,
            'type': {"ext": "html", "mime": mime},
            'date_created': date,
            'date_retrieved': self.dateYMD,
            'license': licenca,
        }
