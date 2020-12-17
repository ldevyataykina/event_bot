import logging
from typing import List
import re

import numpy as np
import requests
from bs4 import BeautifulSoup

from config import UrlForParser, ParserParams

logging.basicConfig(level=logging.INFO)

def get_proxies_list(url) -> List:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    try:
        # proxies = soup.findAll('textarea', class_='form-control')
        # assert proxies != [], "No data! Invalid tag type or class name"
        # proxies_list = proxies[0].text.split('\n\n')[1].split()
        if url == 'https://www.proxyscan.io':
            proxies_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\n\d{2,5}', soup.get_text())
            proxies_list = [proxy.replace('\n', ':') for proxy in proxies_list]
        else:
            proxies_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', soup.get_text())
        assert proxies_list != [], f"No data! Check the link: {url}"
        logging.info("Proxies were successfully parsed")
        return proxies_list
    except Exception as e:
        logging.info(f"Error at proxy parser: {e}")

def get_valid_proxy(proxy_item, test_url, used):
    # Test connection
    try:
        if proxy_item in used:
            return False
        r = requests.get(test_url,
                         proxies={'http': f'http://{proxy_item}', 'https': f'https://{proxy_item}'},
                         timeout=3)
        if r.status_code == 200:
            logging.info("Valid proxy was found!")
            return proxy_item
        else:
            used.append(proxy_item)
            return False
    except:
        used.append(proxy_item)
        return False

def grab_ua(url, path_to_save):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    ua_list = [ua.a.get_text() for ua in soup.findAll('li')]

    with open(path_to_save, 'w') as f:
        for ua_sample in ua_list:
            f.write('%s\n' % ua_sample)

def get_random_ua():
    random_ua = ''
    ua_file = ParserParams.ua_file_path
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_ua = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua

if __name__ == "__main__":
    # ua_list = grab_ua(ParserParams.ua_url, ParserParams.ua_file_path)

    print(get_random_ua())

    # proxies_list = get_proxies_list('https://www.proxyscan.io')
    # for proxy in proxies_list:
    #     print(f"{proxy} - {get_valid_proxy(proxy, UrlForParser.test_url_proxy, [])}")
