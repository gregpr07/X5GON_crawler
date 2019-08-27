from bs4 import BeautifulSoup
import scrapy
from scrapy import Selector
from datetime import datetime
import re
import logging
import requests


class X5Spider(scrapy.Spider):
    name = "engageNYspider"

    baseurl = f'https://www.engageny.org'

    provider = 'engageny.org'

    start_urls = [
        f'{baseurl}',
    ]

    dateYMD = str(datetime.now().strftime("%Y-%m-%d"))

    def parse(self, response):
        to_visit = response.css(
            '.pane-content #mini-panel-common_core_curriculum a::attr(href)').getall()

        # ALL BOOKS
        for book in to_visit:
            yield response.follow(book, callback=self.parseBook)
        # SINGLE ITEM

        # yield response.follow(to_visit[0], callback=self.parseBook)

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
        format = '%a %m/%d/%Y'  # The format
        time_date = datetime.strptime(date_time, format)
        return time_date.strftime("%Y-%m-%d")

    def parseBook(self, response):

        title = response.css('.pane-title h2.eny-title::text').get()

        if 'lesson' in title.lower():

            file_links = response.css(
                '.table-responsive tbody tr a.view.hidden-xs::attr(href)').getall()
            pdfs = []
            for file_link in file_links:
                html = requests.get(self.baseurl+file_link).content
                bs = BeautifulSoup(html, 'lxml')
                pdfs.append([item['data'] for item in bs.find_all(
                    'object', attrs={'data': True})][0])

            description = ' '.join([self.GetText(x) for x in (
                response.css('.pane-content .field-item').getall())]).replace('\n', ' ').replace('  ', ' ').strip(' ')

            url = response.url
            providerurl = self.provider

            date_created = self.convert(response.css(
                'dl.metatag-dl > dd:nth-child(2)::text').get().strip(' -'))

            licenca = response.css(
                '.meta-cc-image a::attr(href)').get()

            for pdf in pdfs:
                concat = {}
                for word in ['student', 'teacher']:
                    if word in pdf:
                        concat = {'created_for': word}

                content = {
                    'title': title,
                    'description': description,
                    'provider_uri': url,
                    'material_url': pdf.strip('#view=Fit'),
                    'language': 'en',
                    'type': {"ext": "pdf", "mime": "application/pdf"},
                    'date_created': date_created,
                    'date_retrieved': self.dateYMD,
                    'license': licenca,
                }

                content.update(concat)

                yield content

        next_page = response.css(
            '.panel-pane .book-nav-next a::attr(href)').get()

        yield response.follow(next_page, callback=self.parseBook)
