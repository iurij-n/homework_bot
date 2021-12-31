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
ERROR_MESSAGE = ('Отсутствует обязательная переменная окружения: '
                     '{item} Программа принудительно '
                     'остановлена.')

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
    if type(current_timestamp) == float:
        timestamp = current_timestamp
    else:
        timestamp = int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.debug('Попытка получить данные API')
        homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except:
        logger.error('Не удалось получить ответ API')
        raise GetAPIAnswerError('Не удалось получить ответ API')
    else:
        logger.debug('Данные API получены')
    if homework.status_code == 200:
        api_answer = homework.json()
        api_answer_error = None
        api_answer_code = None
        if type(api_answer) == dict:
            api_answer_error = api_answer.get('error')
            api_answer_code = api_answer.get('code')
        if api_answer_error:
            logger.error(f'Ошибка API: {api_answer_error}')
            raise GetAPIAnswerError(api_answer_error)
        if api_answer_code:
            logger.error(f'Ошибка API: {api_answer_code}')
            raise GetAPIAnswerError(api_answer_code)
        return api_answer
    else:
        logger.error('Неверный статус API')
        raise GetAPIAnswerError('Неверный статус API')


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

    if hw_list is None or type(hw_list) != list:
        logger.error('Неверный тип списка домашних заданий')
        raise TypeDictError
    
    return hw_list
        


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
        logger.error('Неизвестный статус домашней работы - '
                     f'{homework_status}')
        raise KeyError('Неизвестный статус домашней работы - '
                       f'{homework_status}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logger.critical(ERROR_MESSAGE.format(item='PRACTICUM_TOKEN'))
    if TELEGRAM_TOKEN is None:
        logger.critical(ERROR_MESSAGE.format(item='TELEGRAM_TOKEN'))
    if TELEGRAM_CHAT_ID is None:
        logger.critical(ERROR_MESSAGE.format(item='TELEGRAM_CHAT_ID'))
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
            print('response: ', response)
            homework = check_response(response)
            current_timestamp = response['current_date']
            print('current_timestamp = ', current_timestamp, 'type - ', type(current_timestamp))
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
        except KeyError as error:
            logger.error('Не удалось получить время запроса. '
                         f'Ошибка: {error.__doc__}')
            current_timestamp = int(time.time())
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

        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
