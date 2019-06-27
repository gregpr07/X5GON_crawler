import scrapy


class X5Spider(scrapy.Spider):
    name = "x5spider"

    page = ''
    #baseurl = 'https://eucbeniki.sio.si/mat8/787/index.html'
    baseurl = 'https://eucbeniki.sio.si'

    start_urls = [
        f'{baseurl}',
    ]

    def parse(self, response):
        to_visit = response.css('.ucbenik a::attr(href)').getall()

        for ucbenik in to_visit:
            yield response.follow(ucbenik, callback=self.gifClick)

    def gifClick(self, response):
        ucbenik = response.css(
            'section.summary a.interaktivnaNaloga::attr(href)').get()
        yield response.follow(ucbenik, callback=self.parseBook)

    def parseBook(self, response):
        path = response.css('span.unit-path::text').get().replace('\n', '')

        url = response.url
        providerurl = response.urljoin('../')

        li = response.css('.container li::text').getall()
        p = response.css('.container p::text').getall()
        td = response.css('.container td::text').getall()
        b = response.css('.container b::text').getall()
        ostalo = [x for x in response.css(
            '.container div::text').getall() if len(x) > 6]

        title = response.css('.container h1::text').get()
        important = response.css('.container h3::text').getall()

        imgs = response.css('.container img::attr(src)').getall()
        videos = response.css('.container video::attr(src)').getall()
        audios = response.css('.container audio::attr(src)').getall()

        absimgs = [response.urljoin(x) for x in imgs]
        absvideos = [response.urljoin(x) for x in videos]
        absaudios = [response.urljoin(x) for x in audios]

        licenca = response.css('#show_cclicenca a::attr(href)').get()

        content_unfiltered = p+important+b+li+td+ostalo
        content = ''.join([x.replace('\n', '').replace('\r', '').replace('\t', '').replace('  ', '')
                           for x in content_unfiltered if len(x) > 7])

        yield {
            'title': title,
            'path': path,
            'url': url,
            'provider_url': providerurl,
            'content': content,
            'license': licenca,
            'resources': {'imgs': absimgs, 'videos': absvideos, 'audios': absaudios}
        }
        next_page = response.css('.paging-right a::attr(href)').get()
        yield response.follow(next_page, callback=self.parseBook)
