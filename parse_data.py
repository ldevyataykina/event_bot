import warnings
warnings.simplefilter('ignore')

import time
import os
import yaml
from tqdm import tqdm

from config import AccessInfo, UrlForParser
from db import DataBase
from parser import Afisha_Yandex_Parser
import proxy_parser
from utils import geo, str_to_date

access_info = yaml.full_load(open(AccessInfo.config_file, 'r'))

# Инициализация объекта базы данных для записи и извлечения данных
db = DataBase(access_info['db_params'], access_info['db_info'])

def parse(url, city):
    proxies_list = proxy_parser.get_proxies_list(UrlForParser.proxies)

    for n, proxy_item in enumerate(proxies_list):
        try:
            # Парсинг данных
            parser = Afisha_Yandex_Parser(url=url)
            items = parser.parse_page(proxy=proxy_item,
                                      ua=proxy_parser.get_random_ua())

            if items == 'captcha_error':
                raise ConnectionError(f'captcha was caught. Changing proxy')

            if not items:
                return 'Done'

            items_info = parser.parse_data(items)

            if set(items_info['ids']).issubset(all_ids):

                return "All events have already written to the DataBase"

            existed_ids = [items_info['ids'].index(id) for id in items_info['ids'] if id in all_ids]

            for k, v in items_info.items():
                for i in existed_ids:
                    del v[i]

            items_info['geo'] = [geo(addr) if addr else "" for addr in items_info['places']]
            items_info['date'] = [str_to_date(date) for date in items_info['dates']]
            items_info['event_type'] = [link.rsplit('/', 2)[1] for link in items_info['links']]

            for sample in tqdm(list(zip(*items_info.values()))):
                # if sample[5] in all_ids:
                #     continue

                sample = list(sample)
                db.add_data(
                    event_id=sample[5],
                    event_type=sample[8],
                    event_name=sample[0],
                    start_date=sample[7],
                    start_time=sample[7].time() if type(sample[7]) != str else sample[7],
                    description='NULL',
                    price=sample[3] if sample[3] else 'NULL',
                    city=city,
                    address=sample[2] if sample[2] else 'NULL',
                    latitude=sample[6][0] if sample[6] else 'NULL',
                    longitude=sample[6][1] if sample[6] else 'NULL',
                    contacts=sample[4] if sample[4] else 'NULL'
                )
            return True

        except Exception as e:
            print(e)
            time.sleep(30)
            continue

if __name__ == '__main__':
    for city in UrlForParser.cities:
        print(f'City: {city}')
        all_ids = db.get_id(city)
        print(all_ids)

        # URLS
        afisha_ya_url = os.path.join(UrlForParser.afisha_yandex_main,
                                     city,
                                     'events?page=1')
        print(parse(afisha_ya_url, city))