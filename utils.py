import re
from datetime import datetime
from typing import List

from geopy.geocoders import Nominatim
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pymorphy2
import nltk
nltk.download('punkt')
from nltk import word_tokenize
import pymystem3
from whenareyou import get_tz
import pytz

from config import ParserParams

def geo(addr: str):
    geolocator = Nominatim(user_agent=ParserParams.headers['User-Agent'])
    try:
        location = geolocator.geocode(addr)
        return [location.latitude, location.longitude]
    except:
        return None

MONTH_DICT = {u'январь': 'january', u'февраль': 'february', u'март': 'march', u'апрель': 'april',
              u'май': 'may', u'июнь': 'june', u'июль': 'july', u'август': 'august', u'сентябрь': 'september',
              u'октябрь': 'october', u'ноябрь': 'november', u'декабрь': 'december'}
STOP_WORDS = ['сегодня', 'завтра', 'ср', 'пт', 'сб', 'вс']
morph = pymorphy2.MorphAnalyzer()
mystem = pymystem3.Mystem()

def str_to_date(s: str):
    try:
        # s = re.sub(r'|'.join(map(re.escape, STOP_WORDS)), '', s)
        # s = ' '.join([''.join(mystem.lemmatize(word)[:-1]) for word in word_tokenize(s)])
        s = re.search(r'[А-Яа-я0-9\s]+, \d{,2}:\d{,2}', s)[0]
        s = ' '.join([''.join(mystem.lemmatize(word)[:-1]) for word in word_tokenize(s)])
        month = re.search(r'[А-Яа-я]+', s)[0]
        s = s.replace(month, MONTH_DICT[month.lower()])
        if ' и ' in s:
            s = re.sub(r'и \d+ ', '', s)
        date = parser.parse(s)
        if date < datetime.now():
            date = date + relativedelta(years=1)
        return date
    except Exception as e:
        return 'NULL'

def get_local_time(geo):
    tz = str(get_tz(geo[0], geo[1]))
    tz = pytz.timezone(tz)
    return datetime.now(tz)

def output_transformer(data: List[List]) -> str:
    name_emoji = '⚡️'
    date_emoji = '⏰'
    price_emoji = '💰'
    place_emoji = '🏛'
    distance_emoji = '🚶🏽'
    description_emoji = '🔎'
    contacts_emoji = '📞'

    output_text = []
    for sample in data:
        name = f'{name_emoji} {sample[1]}'
        date = f'{date_emoji} {str(sample[12])}'
        price = f'{price_emoji} {sample[5]}'
        place = f'{place_emoji} {sample[7]}'
        distance = f'{distance_emoji} {str(round(sample[11], 1))}'
        description = f'{description_emoji}' + ' ' + '-' if not sample[4] else sample[4]
        contacts = f'{contacts_emoji} {sample[10]}'

        output = '\n'.join([name, date, price, place, distance, description, contacts])
        output_text.append(output)

    output_text = '\n\n\n'.join(output_text)
    return output_text

if __name__ == "__main__":
    print(get_local_time([60.80634, 37.60869]))
    lst = ['26 сентября', 'сб 19 сентября', '25 октября, 19:00', 'завтра 15 сентября', '27 сентября', 'июль 2021', '21 сентября', '30 сентября', '5 декабря, 19:00', '23 октября, 19:00', 'сб 19 сентября', '8 ноября, 19:00']
    for date in lst:
        print(date)
        print(str_to_date(date), '\n')
