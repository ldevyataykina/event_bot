import yaml
import telebot
from telebot import types

from config import AccessInfo
from db import DataBase
from utils import output_transformer

access_info = yaml.full_load(open(AccessInfo.config_file, 'r'))

# Инициализация объекта базы данных для записи и извлечения данных
db = DataBase(access_info['db_params'], access_info['db_info'])

bot = telebot.TeleBot(access_info['token'])
print('start')

@bot.message_handler(commands=['start'])
def start_dialog(message):
    print('start dialog')
    username = message.from_user.username
    bot.send_message(message.chat.id,
                     f"Привет, {username}")

@bot.message_handler(commands=["search"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Поделиться местоположением", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Чтобы начать поиск, мне сначала нужно узнать, где ты находишься",
                     reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        latitude = message.location.latitude
        longtitude = message.location.longitude

        output_data = db.extract_data([latitude, longtitude])
        output_data = output_transformer(output_data)
        bot.send_message(message.chat.id, output_data)

    else:
        bot.send_message(message.chat.id, "Необходимо поделиться своей геопозицией")
        return


@bot.message_handler(commands=["add"])
def add_event(message):
    db.add_data(event_name="30-летие петуха",
                start_date="2020-08-29",
                start_time="12:00",
                end_time="22:00",
                length=1,
                description="Вечериночка",
                price=5000,
                address="Конаково",
                contacts="+123456")

if __name__ == "__main__":
    bot.polling(none_stop=True)

