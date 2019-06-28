from bs4 import BeautifulSoup
import scrapy
from datetime import datetime
import re


class X5Spider(scrapy.Spider):
    name = "x5spider"

    page = ''
    # baseurl = 'https://eucbeniki.sio.si/mat8/787/index.html'
    baseurl = 'https://eucbeniki.sio.si'
    provider = baseurl.replace('https://', '')

    start_urls = [
        f'{baseurl}',
    ]
    dateYMD = str(datetime.now().year)+"-" + \
        str(datetime.now().month)+"-"+str(datetime.now().day)

    def parse(self, response):
        to_visit = response.css('.ucbenik a::attr(href)').getall()

        # ALL BOOKS
        # for ucbenik in to_visit:
        #    yield response.follow(ucbenik, callback=self.gifClick)
        # SINGLE ITEM
        yield response.follow(to_visit[0], callback=self.gifClick)

    def gifClick(self, response):
        ucbenik = response.css(
            'section.summary a.interaktivnaNaloga::attr(href)').get()
        yield response.follow(ucbenik, callback=self.parseBook)

    def GetText(self, source):
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

    def parseBook(self, response):
        path = response.css('span.unit-path::text').get().replace('\n', '')
        title = re.findall("\|\s((\w)+(\s\w+)*)", path)[1][0]
        url = response.url
        providerurl = response.urljoin('../')
        licenca = response.css('#show_cclicenca a::attr(href)').get()

        text_left = self.GetText(response.css('.page.page-left').get())
        text_right = self.GetText(response.css('.page.page-right').get())

        #title1 = response.css('.container h1::text').get()

        imgs = response.css('.container img::attr(src)').getall()
        videos = response.css('.container video::attr(src)').getall()
        audios = response.css('.container audio::attr(src)').getall()
        absimgs = [response.urljoin(x) for x in imgs]
        absvideos = [response.urljoin(x) for x in videos]
        absaudios = [response.urljoin(x) for x in audios]

        yield {
            'title': title,
            'description': text_left+text_right,
            'resources': {'imgs': absimgs, 'videos': absvideos, 'audios': absaudios},
            'path': path,
            'provider_uri': self.provider,
            'sub_url': providerurl,
            'material_url': url,
            'language': 'sl',
            'type': {"ext": "html", "mime": "text/html"},
            'date_created': self.dateYMD,
            'license': licenca,
        }
        next_page = response.css('.paging-right a::attr(href)').get()

        # DISABLE ALL PAGES
        yield response.follow(next_page, callback=self.parseBook)


'''        important = response.css('.container h3::text').getall()
    li = response.css('.container li::text').getall()
    p = response.css('.container p::text').getall()
    td = response.css('.container td::text').getall()
    b = response.css('.container b::text').getall()
    ostalo = [x for x in response.css(
        '.container div::text').getall() if len(x) > 6]

    content_unfiltered = p+important+b+li+td+ostalo
    content = ' '.join([x.replace('\n', '').replace('\r', '').replace('\t', '').replace('  ', '')
                        for x in content_unfiltered if len(x) > 7])'''
