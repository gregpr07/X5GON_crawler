from scrapy import Selector
import scrapy
import datetime
import re
import json


def convert(date_time):
    format = '%b %d, %Y'  # The format
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str


processed_json = []

with open('v1.json') as json_file:
    data = json.load(json_file)
    count = 0
    for line in data:
        count += 1

        language = re.findall('"code":"(..)"',
                              line['unproccesed']['language'])[0]

        licenca = Selector(text=line['unproccesed']['license']).css(
            'a::attr(href)').get()

        date = Selector(text=line['unproccesed']['first publication date'])
        time = convert(date.css('div::text').get())
        date_created = str(time.year)+('-')+str(time.month)+('-')+str(time.day)

        s_json = {
            'title': line['title'],
            'description': line['description'],
            'provider_uri': line['provider_uri'],
            'material_url': line['material_url'],
            'language': language,
            'type': line['type'],
            'date_created': date_created,
            'license': licenca
        }

        print(count)

        processed_json.append(s_json)

print('writing to file')

with open('processed.json', 'w', encoding='utf-8') as f:
    json.dump(processed_json, f, indent=2)

print('done!')
