# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from scrapy.selector import Selector
import scrapy
from datetime import datetime
import logging
import time

from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)


class X5Spider(scrapy.Spider):
    name = "cnx_spider"

    baseurl = 'https://cnx.org'
    provider = baseurl.replace('https://', '')

    start_urls = [
        f'{baseurl}',
    ]

    dateYMD = str(datetime.now().year)+"-" + \
        str(datetime.now().month)+"-"+str(datetime.now().day)

    # load CHROME headless
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')

    driver = webdriver.Chrome(options=options)
    driver.get(baseurl)
    wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, ".books .book")))

    to_visit = Selector(text=driver.page_source).css(
        '.books .book h3 a::attr(href)').getall()

    def parse(self, response):

        # ALL BOOKS
        for ucbenik in self.to_visit:
            yield response.follow(ucbenik, callback=self.parseBook)
        # SINGLE ITEM
        #yield response.follow(self.to_visit[0], callback=self.parseBook)

    def GetText(self, source):
        try:
            soup = BeautifulSoup(source, "lxml")
            for script in soup(["script", "style", "video", "button", "input", "h2"]):
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

    def parseBook(self, response):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        driver = webdriver.Chrome(options=options)
        driver.get(response.url)

        wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".media-footer #metadata-tab")))
        # open meatadata
        driver.find_element_by_css_selector(
            '.media-footer #metadata-tab').click()
        wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.book-page-toggle button:nth-child(2)")))

        driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[4]/div/div/button[2]').click()

        previous_url = ''
        current_url = ''

        while True:
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#content .main .media-body #content")))

            current_url = driver.current_url
            if current_url != previous_url:
                previous_url = current_url
            else:
                break

            metadata_html_dl = driver.find_element_by_css_selector('.dl-horizontal.dl-metadata').get_attribute('innerHTML')
            html = Selector(text=metadata_html_dl)
            dts = html.css('dt').getall()
            dds = html.css('dd').getall()
            dts_txt = [self.GetText(x).replace(':','').lower() for x in dts]
            dictionary = {}
            for i in range(len(dts_txt)):
                dictionary[dts_txt[i]] = dds[i]


            title = self.GetText(dictionary['name'])


            content = driver.find_element_by_css_selector(
                '#content .main .media-body #content')
            text = self.GetText(content.get_attribute('innerHTML'))

            driver.find_element_by_css_selector('.nav.next').click()

            yield {
                'title': title,
                'provider_uri': self.baseurl,
                'material_url': current_url,
                'description': text,
                'date_retrieved': self.dateYMD,
                'type': {"ext": "html", "mime": "text/html"},
                'unproccesed': dictionary
            }

        driver.close()
