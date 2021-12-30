import os
import time
import logging
import sys


import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (GetAPIAnswerError,
                        EmptyDictError,
                        KeyHomeworksError,
                        TypeDictError,
                        HomeworkTypeError)

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
formatter = logging.Formatter('%(asctime)s - %(levelname)s - '
                              '%(funcName)s - line: %(lineno)d - %(message)s')
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
    homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if homework.status_code == 200:
        return homework.json()
    else:
        raise GetAPIAnswerError


def check_response(response) -> list:
    """Возвращает список домашних работ."""
    if len(response) == 0:
        logger.error('API вернул пустой словарь')
        raise EmptyDictError

    try:
        hw_list = response['homeworks']
    except KeyError:
        logger.error('Не удалось извлечь список домашних работ.')
        raise KeyHomeworksError
    if hw_list is not None and type(hw_list) == list:
        return hw_list
    else:
        logger.error('Неверный тип списка домашних заданий')
        raise TypeDictError


def parse_status(homework):
    """Статус проверки домашней работы."""
    if type(homework) != dict:
        raise HomeworkTypeError
    try:
        homework_name = homework['homework_name']
    except Exception:
        raise KeyError
    try:
        homework_status = homework['status']
    except Exception:
        raise KeyError
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception:
        raise KeyError
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    error_message = ('Отсутствует обязательная переменная окружения: '
                     '{item} Программа принудительно '
                     'остановлена.')
    if PRACTICUM_TOKEN is None:
        logger.critical(error_message.format(item='PRACTICUM_TOKEN'))
    if TELEGRAM_TOKEN is None:
        logger.critical(error_message.format(item='TELEGRAM_TOKEN'))
    if TELEGRAM_CHAT_ID is None:
        logger.critical(error_message.format(item='TELEGRAM_CHAT_ID'))
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    get_api_answer_err = ''
    check_response_err = ''
    if not check_tokens():
        message = 'Нет доступа к переменным окружения. Аварийная остановка.'
        logger.critical(message)
        raise SystemExit(0)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
        except GetAPIAnswerError as error:
            message = ('Не удалось получить ответ API. '
                       f'Ошибка: {error.__doc__}')
            logger.error(message)
            if get_api_answer_err != error.__doc__:
                send_message(bot, message)
                get_api_answer_err = error.__doc__
            time.sleep(RETRY_TIME)
            continue
        except (EmptyDictError, KeyHomeworksError, TypeDictError) as error:
            message = ('Не удалось распознать ответ API. '
                       f'Ошибка: {error.__doc__}')
            logger.error(message)
            if check_response_err != error.__doc__:
                send_message(bot, message)
                check_response_err = error.__doc__
            time.sleep(RETRY_TIME)
            continue
        else:
            get_api_answer_err = ''
            check_response_err = ''
            logger.debug(f'Ответ API {response}')
            logger.debug(f'Список домашних работ {homework}')

        if len(homework) != 0:
            for hw in homework[::-1]:
                send_message(bot, parse_status(hw))
                logger.debug('Получен новый статус')
        else:
            logger.debug('Новых статусов нет')

        current_timestamp = int(time.time())
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
