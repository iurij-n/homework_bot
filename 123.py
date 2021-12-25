from pprint import pprint
import requests
import time
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

TOKEN = 'AQAAAAASWs4aAAYckVnFE8x9YEaii-cSMWqvmBo'
TELEGRAM_TOKEN = '5012792175:AAEeMJx4s2t3WQbMcfaX82DQ9qF8SzR23-4'
TELEGRAM_CHAT_ID = 537063134
url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {TOKEN}'}
payload = {'from_date': 1610103324}


bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN)

text = 'Вам телеграмма!'
# Отправка сообщения
bot.send_message(TELEGRAM_CHAT_ID, text)

# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)

# Печатаем ответ API в формате JSON
#print(homework_statuses.text)

# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
print('Текущее время - ', int(time.time()))
type_answer = type(homework_statuses.json())
print('Тип данных ответа API - ', type_answer)
print(isinstance(type_answer, dict))
if isinstance(homework_statuses.json(), dict):
    print('Тип ответа словарь')
pprint(homework_statuses.json())
pprint(homework_statuses.json().get('homeworks'))


# response = requests.get('https://www.swapi.tech/api/starships/9/')
# pprint(response.json())
#print(response.json().get('result').get('properties').get('name'))

if len(homework_statuses.json().get('homeworks')) != 0:
    print(homework_statuses.json().get('homeworks')[0].get('status'))