import os
import re
import json
import redis
import random
import logging

import vk_api as vk
from time import sleep
from dotenv import load_dotenv
from logs_handler import TelegramLogsHandler
from fetch_questions import fetch_random_questions
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


logger = logging.getLogger(__name__)
exception_logger = logging.getLogger('exception_logger')


def start(event, vk_api, keyboard):
    """Send a  greeting message."""
    logger.info(f'Пользователь {event.user_id} запустил бота.')

    greetings = 'Приветствую! \nЯ бот задающий ' \
                'интересные вопросы. \nНу что поиграем? 🎲.'

    vk_api.messages.send(
        user_id=event.user_id,
        message=greetings,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def ask_question(event, vk_api, keyboard, redis_client):
    user_id = event.user_id

    quiz_question = fetch_random_questions()
    question = re.sub(r'Вопрос \d+:\s+', '', quiz_question[0])
    answer = re.sub(r'Ответ:\s+', '', quiz_question[1])

    redis_client.set(f'{user_id}_question', json.dumps(question))
    redis_client.set(f'{user_id}_answer', json.dumps(answer))

    question = json.loads(redis_client.get(f'{user_id}_question'))

    logger.info(f'question--->{question}, \nanswer--->{answer}')

    question_text = f'Внимание вопрос: \n\n{question}'

    vk_api.messages.send(
        user_id=event.user_id,
        message=question_text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def check_answer(event, vk_api, keyboard, redis_client):
    user_id = event.user_id
    answer = json.loads(redis_client.get(f'{chat_id}_answer')).split('.')[0]
    lower_answer = answer.lower()

    if event.text.lower() == lower_answer:
        try:
            total_score = json.loads(redis_client.get(f'{user_id}_score'))
        except TypeError:
            total_score = 0
        redis_client.set(f'{user_id}_score', total_score + 1)
        bot_answer = 'Правильно! Поздравляю! Для следующего вопроса нажми ' \
                     '«Новый вопрос»'
    else:
        bot_answer = 'Неправильно… Попробуешь ещё раз?'

    vk_api.messages.send(
        user_id=event.user_id,
        message=bot_answer,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def show_answer(event, vk_api, keyboard, redis_client):
    user_id = event.user_id
    answer = json.loads(redis_client.get(f'{user_id}_answer'))
    bot_answer = f"Правильный ответ \n\n{answer}\n\n"
    vk_api.messages.send(
        user_id=event.user_id,
        message=bot_answer,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )
    ask_question(event, vk_api, keyboard, redis_client)


def check_score(event, vk_api, keyboard, redis_client):
    user_id = event.user_id
    total_score = json.loads(redis_client.get(f'{user_id}_score'))
    bot_answer = f"Ваш общий итоговый счет {total_score} балл(а/ов)"

    vk_api.messages.send(
        user_id=event.user_id,
        message=bot_answer,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def main(event, vk_api, redis_client):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос ❔', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться ❌', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет ✍️', color=VkKeyboardColor.PRIMARY)

    if event.text == 'Новый вопрос ❔':
        ask_question(event, vk_api, keyboard, redis_client)
    elif event.text == 'Старт':
        start(event, vk_api, keyboard)
    elif event.text == 'Сдаться ❌':
        show_answer(event, vk_api, keyboard, redis_client)
    elif event.text == 'Мой счет ✍️':
        check_score(event, vk_api, keyboard, redis_client)
    else:
        check_answer(event, vk_api, keyboard, redis_client)


if __name__ == "__main__":
    load_dotenv()
    TIMEOUT = 120
    vk_session = vk.VkApi(token=os.getenv("VK_API_TOKEN"))
    chat_id = os.getenv('TG_CHAT_ID')
    api_tg_token = os.getenv('TG_API_BOT')

    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                               '%(message)s', datefmt='%d-%m-%Y %I:%M:%S %p',
                        level=logging.INFO)

    exception_logger.setLevel(logging.ERROR)
    exception_logger.addHandler(TelegramLogsHandler(api_tg_token, chat_id))

    with redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=0,
            password=os.getenv("REDIS_PASSWORD")
    ) as redis_client:
        while True:
            try:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        main(event, vk_api, redis_client)
            except Exception:
                exception_logger.exception("Бот упал с ошибкой")
                sleep(TIMEOUT)
