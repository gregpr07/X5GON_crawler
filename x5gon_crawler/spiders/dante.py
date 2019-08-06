from bs4 import BeautifulSoup
import scrapy
from datetime import datetime


class X5Spider(scrapy.Spider):
    name = "danteCrawler"

    baseurl = 'https://www2.colegiodante.com.br/rea/lista.php?pag='

    provider = 'colegiodante.com'

    start_urls = [
        baseurl+str(1),
    ]

    dateYMD = str(datetime.now().year)+"-" + \
        str(datetime.now().month)+"-"+str(datetime.now().day)

    def parse(self, response):
        for i in range(2, 13):
            response.follow(self.baseurl+str(i), callback=self.loop)

    def loop(self, response):
        to_visit = response.css('.lista_conteudo h2 a::attr(href)').getall()
        for link in to_visit:
            yield response.follow(link, callback=self.parseBook)

    def parseBook(self, response):

        title = response.css('#central > h1:nth-child(1)::text').get()
        description = self.GetText(response.css('.conteudo_descricao').get())

        file_link = response.css(
            '.conteudo_display > a:nth-child(1)::attr(href)').getall()

        url = response.url
        providerurl = self.provider

        licenca = response.css(
            'a.cc::attr(href)').get()

        content = {
            'title': title,
            'description': description,
            'provider_uri': url,
            'material_url': file_link,
            'language': 'pt',
            'type': {"ext": "html", "mime": "text/html"},
            'date_retrieved': self.dateYMD,
            'license': licenca,
        }

        yield content

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
