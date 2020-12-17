
class AccessInfo:
    config_file = "./data/config.yaml"

class EventTableColumns:
    event_id = "event_id"
    event_name = "event_name"
    start_date = "start_date"
    start_time = "start_time"
    end_date = "end_date"
    end_time = "end_time"
    # length = "length"
    description = "description"
    price = "price"
    city = "city"
    address = "address"
    latitude = "latitude"
    longitude = "longitude"
    contacts = "contacts"
    event_type = "event_type"

class UrlForParser:
    proxies = "https://www.us-proxy.org" # "https://www.proxyscan.io"
    test_url_proxy = "https://www.google.com/"
    afisha_yandex_main = "https://afisha.yandex.ru"
    cities = ["moscow", "saint-petersburg"]
    afisha_yandex = "https://afisha.yandex.ru/moscow/events?page=1"

class ParserParams:
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'}
    ua_url = 'http://useragentstring.com/pages/useragentstring.php?name=All'
    ua_file_path = './data/ua.txt'
    driver_path = './drivers/chromedriver'

# class DataInfo:
#     event_types = {
#         'art': '',
#         'ballet': '',
#         'cinema': '',
#         'cinema_show': '',
#         'circus_show': '',
#         'concert': '',
#         'conference': '',
#         'excursions': '',
#         'festival': '',
#         'immersive - theatre': '',
#         'kids': '',
#         'lectures': '',
#         'literary - reading'
#         | literaryevent |
#         | meeting |
#         | mobiletheater |
#         | monoperformance |
#         | musical |
#         | musical - play |
#         | ny_matinee |
#         | opera |
#         | operetta |
#         | other |
#         | party |
#         | performance |
#         | plastical_performance |
#         | puppets |
#         | recital |
#         | show |
#         | sport |
#         | standup |
#         | theatre |
#         | theatre_show
#     }