import json
import requests
from scrapy import Selector

json_file = open('data_oerhoernchen20-highereducation_0_19509.json', 'r')
json_read = json.load(json_file)

all_repos = {}

# parse TIBAv


def parseTIBAV():
    OUTPUT_LOCATION = ''
    jsonname = 'parsed.json'

    with open(OUTPUT_LOCATION+jsonname, 'w+', encoding='utf-8') as f:
        f.write('[\n')
        i = 0
        parsedREPO = []
        content = {}
        for material in json_read:
            content = {}
            i += 1
            print('-----', str(i), '-----')
            try:
                if material['projectkey'] == 'tibav':
                    material_link = material["main_url"]

                    raw_html = requests.get(material_link).text
                    selector_html = Selector(text=raw_html)

                    material_url = 'http:'+selector_html.css(
                        'video source::attr(src)').get()

                    language = selector_html.css(
                        '.table td.value div::attr(lang)').get()

                    try:
                        description = material["description"]
                    except:
                        description = ''

                    content = {
                        'title': material["title"],
                        'description': description,
                        'provider_uri': material["main_url"],
                        'material_player': material_link.replace('media', 'player'),
                        'material_url': material_url,
                        'language': language,
                        'type': {"ext": "mp4", "mime": "video/mp4"},
                        # 'date_created': date_created,
                        # 'date_retrieved': self.dateYMD,
                        'license': material["license_url"]
                    }
            except Exception as e:
                print('\033[93mEXCEPTION:', e)
                print('\033[92m...continuing with the loop\033[0m\n')

            json.dump(content, f, indent=2)
            print('appended to json')
            f.write(',\n')
            # break

        f.write('\n]')


parseTIBAV()
