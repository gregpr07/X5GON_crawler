import scrapy


class X5Spider(scrapy.Spider):
    name = "x5spider"

    page = ''
    baseurl = 'https://eucbeniki.sio.si/mat8/787/index4.html'

    start_urls = [
        f'{baseurl}',
    ]

    to_visit = []

    def parse(self, response):
        path = response.css('span.unit-path::text').get()
        url = response.url

        li = response.css('.container li::text').getall()
        p = response.css('.container p::text').getall()
        td = response.css('.container td::text').getall()
        b = response.css('.container b::text').getall()
        ostalo = [x for x in response.css(
            '.container div::text').getall() if len(x) > 6]

        title = response.css('.container h1::text').getall()
        important = response.css('.container h3::text').getall()

        imgs = response.css('.container img::attr(src)').getall()
        videos = response.css('.container video::attr(src)').getall()
        audios = response.css('.container audio::attr(src)').getall()

        licenca = response.css('#show_cclicenca a::attr(href)').get()

        content_unfiltered = p+important+b+li+td+ostalo
        content = ''.join([x.strip('\n').strip('\r').strip('\t').strip('  ')
                           for x in content_unfiltered if len(x) > 7])

        yield {
            'title': title,
            'path': path,
            'url': url,
            'content': content,
            'license': licenca,
            'resources': {'imgs': imgs, 'videos': videos, 'audios': audios}
        }
