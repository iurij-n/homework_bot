import os
import time
import logging
import sys


import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
RETRY_TIME = 600
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Бот отправил сообщение: {message}')
    except Exception as error:
        logger.error(f'Бот не смог отправить сообщение: {error}')


def get_api_answer(current_timestamp):
    """Запрос к API-сервиса проверки домашней работы."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logger.debug(f'Код ответа API: {homework.status_code}')
    #logger.debug(f'Тип кода ответа API: {type(homework.status_code)}')
        if homework.status_code != 200:
            logger.error(f'Сбой в работе программы. '
                        f'Код ответа API: {homework.status_code}')
            return False 
        else:
            logger.debug(f'get_api_answer вернула {homework.json()}')
            return homework.json()
    except Exception:
        logger.error(f'Сбой в работе программы. '
                        f'Код ответа API: {homework.status_code}')
        return False


def check_response(response) -> list:
    """Возвращает список домашних работ."""
    if isinstance(response, dict):
        logger.debug('Получен список домашних работ')
        try:
            hw_list = response.get('homeworks')
            logger.debug('Список домашних работ извлечен успешно')
            return hw_list
        except Exception:
            logger.error('Не удалось извлечь список домашних работ')
    else:
        logger.error(f'Тип данных ответа API {type(response)}. '
                     'Должен быть словарь.')
        return []


def parse_status(homework):
    """Статус проверки домашней работы."""
    homework_name = homework.get('lesson_name')
    if homework_name is None:
        logger.error('Не удалось извлечь название домашней работы')
        homework_name = 'Неизвестная домашняя работа'
    
    homework_status = homework.get('status')
    if homework_status is None:
        logger.error('Неизвесный статус домашней работы')
    else:
        verdict = HOMEWORK_STATUSES.get(homework_status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logger.critical('Отсутствует обязательная переменная окружения: '
                        'PRACTICUM_TOKEN Программа принудительно '
                        'остановлена.')
    if TELEGRAM_TOKEN is None:
        logger.critical('Отсутствует обязательная переменная окружения: '
                        'TELEGRAM_TOKEN Программа принудительно '
                        'остановлена.')
    if TELEGRAM_CHAT_ID is None:
        logger.critical('Отсутствует обязательная переменная окружения: '
                        'TELEGRAM_CHAT_ID Программа принудительно '
                        'остановлена.')
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while check_tokens():
        try:
            try:
                response = get_api_answer(current_timestamp)
            except Exception:
                logger.error('Не удалось получить ответ API')
                send_message(bot, 'Не удалось получить ответ API')
            logger.debug(f'Ответ API {response}')
            try:
                homework = check_response(response)
            except Exception:
                logger.error('Не удалось распознать ответ API')
                send_message(bot, 'Не удалось распознать ответ API')
            logger.debug(f'Список домашних работ {homework}')
            if len(homework) != 0:
                send_message(bot, parse_status(homework[0]))
                logger.debug('Получен новый статус')
            else:
                logger.debug('Новых статусов нет')

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
    else:
        message = 'Переменные окружения не доступны'
        send_message(bot, message)


if __name__ == '__main__':
    main()
