import yaml
import logging
import ssl
from aiohttp import web
import telebot
from telebot import types

from config import AccessInfo
from db import DataBase
from utils import output_transformer

access_info = yaml.full_load(open(AccessInfo.config_file, 'r'))

# Инициализация объекта базы данных для записи и извлечения данных
db = DataBase(access_info['db_params'], access_info['db_info'])

WEBHOOK_HOST = '<ip/host where the bot is running>'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(access_info['token'])

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(access_info['token'])

app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)
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

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)

