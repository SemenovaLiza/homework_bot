import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import MessageNotSendError, VariableNotFoundError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Checks the availability of environment variables."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(tokens):
        logger.critical('Required variable is missing.')
        raise VariableNotFoundError


def send_message(bot, message):
    """Sends a message to Telegram chat."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('A message was sent to Telegram chat.')
    except MessageNotSendError:
        logger.error('A "MessageNotSendError"'
                     'error occurred while sending the message.')
    except Exception as error:
        logger.error(f'A "{error}" error occurred while sending the message.')


def get_api_answer(timestamp):
    """Makes a request to the API service."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.RequestException:
        logger.error('An error occurred while handling request.')
    except requests.ConnectionError:
        logger.error('A connection error occurred.')
    except Exception as error:
        logger.error(f'A {error} occurred.')

    if response.status_code != HTTPStatus.OK:
        raise requests.HTTPError
        logger.error('A HTTP error occurred.')

    response = response.json()
    return response


def check_response(response):
    """Checks the response for compliance with the documentation."""
    if type(response) != dict:
        raise TypeError
        logger.error('Unexpected response type.')
    if type(response.get('homeworks')) != list:
        raise TypeError
        logger.error('Unexpected response.key type.')


def parse_status(homework):
    """Extracts the status and name of homework from response."""
    try:
        homework_name = homework.get('homework_name')
        status = homework.get('status')
        verdict = HOMEWORK_VERDICTS[status]
    except KeyError:
        logger.error('There is no "status" key in the response.')
    if 'homework_name' not in homework:
        raise KeyError
        logger.error('There is no "homwork_name" key in the response.')
    if status not in HOMEWORK_VERDICTS:
        logger.error('An unexpected "status" key value.')
        raise KeyError
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """The main logic of the bot."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    homework_status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if len(response.get('homeworks')) != 0:
                homework = response.get('homeworks')[0]
                if homework_status != parse_status(homework):
                    homework_status = parse_status(homework)
                    send_message(bot, homework_status)
                else:
                    logger.debug('There is no new homwork status.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error('An error occurred while the bot was running.')
            send_message(bot, message)

    time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='homework_bot.log',
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler(stream=sys.stdout)
