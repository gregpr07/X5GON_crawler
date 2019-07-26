from bs4 import BeautifulSoup
import scrapy
from datetime import datetime
import re
import logging


class X5Spider(scrapy.Spider):
    name = "engageNYspider"

    baseurl = f'https://www.engageny.org'

    provider = 'engageny.org'

    start_urls = [
        f'{baseurl}',
    ]

    dateYMD = str(datetime.now().year)+"-" + \
        str(datetime.now().month)+"-"+str(datetime.now().day)

    def parse(self, response):
        to_visit = response.css(
            '.pane-content #mini-panel-common_core_curriculum a::attr(href)').getall()

        # ALL BOOKS
        for book in to_visit:
            yield response.follow(book, callback=self.parseBook)
        # SINGLE ITEM
        
        # yield response.follow(to_visit[0], callback=self.parseBook)

    def ParsePdf(self, response):
        #response.css('.field-content #pdf_reader embed::attr(src)').get()
        logging.warning('what')

    def parseBook(self, response):

        title = response.css('.pane-title h2.eny-title::text').get()
        if 'lesson' in title.lower():
            

            file_links = response.css(
                '.table-responsive tbody tr a.view.hidden-xs::attr(href)').getall()
            pdfs = []
            for file_link in file_links:
                pdfs.append(self.baseurl + file_link)

            url = response.url
            providerurl = self.provider
            licenca = response.css(
                '.meta-cc-image a::attr(href)').get()

            yield {
                'title': title,
                'material_url': url,
                'date_retrieved': self.dateYMD,
                'license': licenca,
                'pdfs': pdfs,
            }

        next_page = response.css(
            '.panel-pane .book-nav-next a::attr(href)').get()

        yield response.follow(next_page, callback=self.parseBook)
