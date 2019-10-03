from bs4 import BeautifulSoup
import scrapy
from datetime import datetime
import logging


class X5Spider(scrapy.Spider):
    name = "siemens_stiftung"

    start = 'https://medienportal.siemens-stiftung.org'

    data = 'https://medienportal.siemens-stiftung.org/portal/main.php?todo=showObjData&objid='

    view = 'https://medienportal.siemens-stiftung.org/view/'

    provider = 'medienportal.siemens-stiftung.org'

    start_urls = [
        start,
    ]

    languages = {
        'German': 'de',
        'English': 'en',
        'Spanish': 'es'
    }

    dateYMD = str(datetime.now().strftime("%Y-%m-%d"))

    def parse(self, response):
        for i in range(100000, 113000):
            yield response.follow(self.data+str(i), callback=self.parsePage, meta={'i': i})

    def GetText(self, source, custom):
        try:
            soup = BeautifulSoup(source, "lxml")
            for script in soup(["script", "style", "video", "button", "input"]+custom):
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
        return str(datetime.now().strftime("%Y-%m-%d"))

    def parsePage(self, response):

        media = response.css('.medientyp::text').get()

        if media == 'Text':

            i = response.meta.get('i')

            title = response.css('.beschreibung h3::text').get()

            pdf = self.view+str(i)

            description = self.GetText(response.css(
                '.kurzinfo').get(), []).strip('Text\n')

            url = response.url
            providerurl = self.provider

            date = self.GetText(response.css(
                '.daten > div:nth-child(4)').get(), ['span'])

            licenca = response.css(
                '.lizenzbox > a:nth-child(3)::attr(href)').get()

            language = self.languages[self.GetText(response.css(
                '.daten > div:nth-child(1)').get(), ['span']).replace(',', '').split()[0]]

            yield {
                'title': title,
                'description': description,
                'provider_uri': url,
                'material_url': str(pdf)+'.pdf',
                'language': language,
                'type': {"ext": "pdf", "mime": "application/pdf"},
                'date_created': date,
                'date_retrieved': self.dateYMD,
                'license': licenca,
            }
