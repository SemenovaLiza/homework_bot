import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler(stream=sys.stdout)

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
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Sends a message to Telegram chat."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(
            f'A message "{message}" was successfully'
            f'sent to user {TELEGRAM_CHAT_ID}.'
        )
    except Exception:
        logger.error('An MessageNotSend error occurred'
                     'while sending a message.')
        raise exceptions.MessageNotSendError(
            (f'A message could not be sent.'
             f'Message context: {message}.'
             f'Telegram chat id: {TELEGRAM_CHAT_ID}'),
            exc_info=True
        )


def get_api_answer(timestamp):
    """Makes a request to the API service."""
    request_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        response = requests.get(**request_params)
        if response.status_code != HTTPStatus.OK:
            raise requests.HTTPError(
                'Failed to connect to the "{url}".'
                'Authorization token: {headers}.'
                'Request param: {params}.'.format(**request_params),
                f'Response status code: {response.status_code}',
                exc_info=True
            )
    except requests.RequestException:
        raise exceptions.InvalidStatusCode(
            'Failed to connect to the "{url}".'
            'Authorization token: {headers}.'
            'Request param: {params}.'.format(**request_params),
            f'Response status code: {response.status_code}',
            exc_info=True
        )
    response = response.json()
    return response


def check_response(response):
    """Checks the response for compliance with the documentation."""
    if type(response) != dict:
        raise TypeError(
            'A type of response differs from the expected one.'
            'Expected: dict',
            exc_info=True
        )
    if type(response.get('homeworks')) != list:
        raise TypeError(
            'A type of response key "homeworks" differs from the'
            'expected one. Expected: list',
            exc_info=True
        )


def parse_status(homework):
    """Extracts the status and name of homework from response."""
    homework_name = homework.get('homework_name')
    if 'homework_name' not in homework:
        raise KeyError(
            'There is no necessary "homework_name" key in the response',
            exc_info=True
        )
    status = homework.get('status')
    if 'status' not in homework:
        raise KeyError(
            'There is no necessary "status" key in the response',
            exc_info=True)
    if status not in HOMEWORK_VERDICTS:
        raise KeyError(
            'Undocumented homework status.',
            exc_info=True)
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """The main logic of the bot."""
    if not check_tokens():
        logger.critical('Required variable is missing.'
                        'The program is stopped.')
        sys.exit('Required variable is missing.')
    else:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time())
        homework_status = ''
        while True:
            try:
                response = get_api_answer(timestamp)
                timestamp = response.get('current_date')
                check_response(response)
                if response.get('homeworks'):
                    homework = response.get('homeworks')[0]
                    if homework_status != parse_status(homework):
                        homework_status = parse_status(homework)
                        send_message(bot, homework_status)
                    else:
                        logger.debug('There is no new homework status.')
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error('An error occurred while the bot was running.')
                send_message(bot, message)
            finally:
                time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='homework_bot.log',
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()
