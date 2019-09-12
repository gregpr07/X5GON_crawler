import json
import re
import requests
from scrapy import Selector
from datetime import datetime

json_file = open('data_oerhoernchen20-highereducation_0_19509.json', 'r')
json_read = json.load(json_file)

all_repos = {}

dateYMD = str(datetime.now().strftime("%Y-%m-%d"))

# parse TIBAv


def parseTIBAV():
    OUTPUT_LOCATION = ''
    jsonname = 'tibav_v2.json'

    with open(OUTPUT_LOCATION+jsonname, 'w+', encoding='utf-8') as f:
        f.write('[\n')
        i = 0
        parsedREPO = []
        content = {}
        for material in json_read:
            content = {}
            i += 1
            if i < 19500:
                continue
            print('-----', str(i), '-----')
            try:
            if material['projectkey'] == 'tibav':
                material_link = material["main_url"]

                raw_html = requests.get(material_link).text
                selector_html = Selector(text=raw_html)

                material_url = selector_html.css(
                    'video source::attr(src)').get()

                language = selector_html.css(
                    '.table td.value div::attr(lang)').get()

                raw_date_find = selector_html.css(
                    'textarea.form-control::text').get()

                date_created = re.findall(
                    'year=\{(\d{4})\}', raw_date_find)[0]
                if date_created:
                    date_created += '-01-01'
                else:
                    date_created = ''

                try:
                    description = material["description"]
                except:
                    description = ''

                content = {
                    'title': material["title"].replace('\n', ' '),
                    'description': description,
                    'provider_uri': material["main_url"],
                    'material_player': material_link.replace('media', 'player'),
                    'material_url': material_url,
                    'language': language,
                    'type': {"ext": "mp4", "mime": "video/mp4"},
                    'date_created': date_created,
                    'date_retrieved': dateYMD,
                    'license': material["license_url"]
                }
            else:
                print('not tibav')
            except Exception as e:
                print('\033[93mEXCEPTION:', e)
                print('\033[92m...continuing with the loop\033[0m\n')

            if content:
                json.dump(content, f, indent=2)
                f.write(',\n')
                print('appended to json')
            else:
                print('content is empty, skipping')

            # break

        f.write('\n]')


parseTIBAV()
