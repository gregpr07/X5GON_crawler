import requests
import datetime
from slugify import slugify
import json

# python3.7 x5gon_crawler/spiders/openlearnware.py

APIurl = 'https://openlearnware.tu-darmstadt.de/olw-rest-db/api/resource-detailview/index/'
resourceURL = 'https://www.openlearnware.de/resource/'

OUTPUT_LOCATION = './crawls/openlearnware/'

jsonname = 'openlearnware_v1.json'

cdn_base = 'https://olw-material.hrz.tu-darmstadt.de/olw-konv-repository/material'

dateYMD = str(datetime.datetime.now().strftime("%Y-%m-%d"))

languages = {1: 'de', 2: 'en'}
# the only languages that exist - data from frontend api - resource.tpl.html


def getExtensions(num):
    charType = {
        1: '13.pdf',
        2: '2.mp4',
        3: '7.mp3',
        4: '1.mp4',
        5: '',
        6: '4.mp4',
        7: '',
        8: '90.mp4',
        9: '30.zip',
        10: '3.mp4',
    }
    if num in charType:
        return charType[num]
    else:
        return '7.mp3'
# the data gathered from api - file olwCdnService.js


def getType(num):
    if num == 1:
        return {"ext": "pdf", "mime": "application/pdf"}
    elif num % 2 == 0:
        return {"ext": "mp4", "mime": "video/mpeg"}
    elif num == 9:
        return {"ext": "zip", "mime": "application/zip"}
    else:
        return {"ext": "mp3", "mime": "audio/mpeg"}
# get type of file from extension bamboozle


def getMaterialLink(uuid, numType):
    uuid = uuid.replace('-', '')

    cnd = '/'
    i = 0
    for letter in uuid:
        i += 1
        cnd += letter
        if not i % 2:
            cnd += '/'
    endLink = getExtensions(numType)

    return (cdn_base+cnd+endLink)
# get material link from their cdn


def convertTime(date_time):
    timestamp = datetime.datetime.fromtimestamp(date_time/1e3)
    return timestamp.strftime("%Y-%m-%d")
# convert int time


with open(OUTPUT_LOCATION+jsonname, 'w+', encoding='utf-8') as f:
    f.write('[\n')
    parent_meta = {}
    for i in range(1, 5000):
        print('-----', str(i), '-----')

        materialID = i
        url = APIurl + \
            str(materialID)

        r_json = requests.get(url).json()
        content = {}
        if r_json and not r_json['deleted'] and r_json['open']:
            try:
                # if material has a parent
                if r_json['parent']:

                    for uuid_loop in parent_meta:
                        # and material uuid equals any meta that is saved
                        if r_json['parent'] == uuid_loop:
                            uuid = r_json['uuid']

                            print('found parent for', uuid)

                            content = parent_meta[uuid_loop]

                            material_url = getMaterialLink(
                                r_json['uuid'], r_json['characteristicType'])

                            typez = getType(r_json['characteristicType'])

                            content['type'] = typez
                            content['material_url'] = material_url

                            content['metadata']['id'] = materialID
                            content['metadata']['uuid'] = uuid
                            content['metadata']['if_child_meta']['parent_uuid'] = r_json['parent']
                            content['metadata']['if_child_meta']['title'] = r_json['name'].replace(
                                '\n', ' ')

                            #parent_meta.pop(uuid_loop, None)

                        else:
                            continue
                # else means that material is a parent
                else:
                    title = r_json['name'].replace(
                        '\n', ' ')
                    uuid = r_json['uuid']

                    material_url = getMaterialLink(
                        r_json['uuid'], r_json['characteristicType'])
                    material_uri = resourceURL + \
                        slugify(title)+'-'+str(materialID)

                    language = languages[int(r_json['languages'][0]['id'])]

                    licensecode = r_json['code']
                    licenca = f'https://creativecommons.org/licenses/{licensecode}/3.0/'
                    # resource.tpl.html - says that there are only 3.0 licences

                    date_created = convertTime(r_json["creationDate"])
                    date_retrieved = dateYMD

                    description = r_json['description'].replace('\n', ' ')

                    areas = r_json['areas']

                    typez = getType(r_json['characteristicType'])

                    content = {
                        'title': title,
                        'description': description,
                        'provider_uri': material_uri,
                        'material_url': material_url,
                        'language': language,
                        'type': typez,
                        'date_created': date_created,
                        'date_retrieved': date_retrieved,
                        'license': licenca,
                        'metadata': {
                            'id': materialID,
                            'uuid': uuid,
                            'areas': areas,
                            'collections': r_json["collections"],
                            'if_child_meta': {
                                'parent_uuid': '',
                                'title': ''
                            }

                        }
                    }

                    if r_json['childs']:
                        parent_meta[uuid] = content

                # ouput
                json.dump(content, f, indent=2)
                print('appended to json')
                f.write(',\n')
            except Exception as e:
                print('\033[93mEXCEPTION:', e)
                print('\033[92m...continuing with the loop\033[0m\n')
                continue

    f.write('\n]')
