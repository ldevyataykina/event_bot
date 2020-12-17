from typing import List
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from config import ParserParams, UrlForParser

# class CaptchaError(ValueError):
#     def __init__(self):
#         return False

class Afisha_Yandex_Parser:
    def __init__(self, url):
        self.url = url

    def parse_page(self, proxy, ua):
        try:
            capabilities = webdriver.DesiredCapabilities.CHROME
            capabilities['marionette'] = True
            capabilities['proxy'] = {
                "proxyType": "MANUAL",
                "httpProxy": proxy
            }

            driver = webdriver.Chrome('./drivers/chromedriver', desired_capabilities=capabilities)
            driver.get(self.url)
            time.sleep(10)

            clicks = 1
            while clicks:
                # start to scroll down
                driver.execute_script("window.scrollBy(0, 300)")
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

                try:
                    # load next page
                    driver.find_element_by_class_name("button2").click()
                    clicks += 1
                    time.sleep(1)
                except NoSuchElementException:
                    print(f'The last page: {clicks}')
                    break
                except Exception as e:
                    print(f'{e} after {str(clicks-1)} clicks')
                    break

        except Exception as e:
            print(clicks, e)
            return None

        if 'Нам очень жаль, но запросы, поступившие с вашего IP-адреса, похожи на автоматические' in driver.page_source:
            return 'captcha_error'

        events = driver.find_elements_by_xpath('//div[contains(@class, "event events-list__item yandex-sans")]')

        if not events:
            events = driver.find_elements_by_xpath('//div[contains(@class, "Root-sc-5meihc-0 fgQjNK")]')

        self.ids = [BeautifulSoup(event.get_attribute('innerHTML'), 'html.parser').div.div['data-event-id']
                    for event in events]

        self.events_price = [BeautifulSoup(price.get_attribute('innerHTML'), 'html.parser').span.get_text(strip=True).replace(u'\xa0', u' ')
                             for price in driver.find_elements_by_xpath('//span[contains(@data-testid, "event-card-price")]')]

        self.events_link = [os.path.join(self.url.rsplit('/', 2)[0], BeautifulSoup(link.get_attribute('outerHTML'), 'html.parser').a['href'][1:])
                            for link in driver.find_elements_by_xpath('//a[contains(@data-testid, "event-card-link")]')]

        events = [BeautifulSoup(event.get_attribute('outerHTML'), 'html.parser').select('div[data-component="EventCard__EventInfo"]')[0]
                  for event in events]
        driver.close()
        return events

    def parse_data(self, events: List):
        places = []
        names = [event.find('h2').text for event in events]
        # dates = [event.find('li', class_='DetailsItem-sc-5meihc-3 jBdNGK').text
        #          if event.find('li', class_='DetailsItem-sc-5meihc-3 jBdNGK') is not None
        #          else event.find('li', class_='DetailsItem-sc-5meihc-3 jmTuPp').text
        #          for event in events]
        dates = [event.find('li').text if event.find('li') is not None else None for event in events]

        for event in events:
            try:
                place = event.findAll('li')[1]['title']
            except:
                place = ''
            places.append(place)

        return {'names': names,
                'dates': dates,
                'places': places,
                'prices': self.events_price,
                'links': self.events_link,
                'ids': self.ids}
