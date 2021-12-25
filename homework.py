import requests
import time
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv()


PRACTICUM_TOKEN = 'AQAAAAASWs4aAAYckVnFE8x9YEaii-cSMWqvmBo'
TELEGRAM_TOKEN = '5012792175:AAEeMJx4s2t3WQbMcfaX82DQ9qF8SzR23-4'
TELEGRAM_CHAT_ID = 537063134

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=secret_token)


def send_message(bot, message):
    ...


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return homework.json()


def check_response(response):
    if isinstance(response, dict):
        return response.get('homeworks')


def parse_status(homework):
    homework_name = homework.get('lesson_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    ...


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
