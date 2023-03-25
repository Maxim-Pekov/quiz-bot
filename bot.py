import json
import logging
import os
from functools import partial

import redis
import random

from dotenv import load_dotenv
from textwrap import dedent
from main import fetch_random_questions

from telegram import ReplyKeyboardMarkup
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


QUESTION = 1
ANSWER = 2


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    greetings = dedent(fr'''
                            Приветствую {user.mention_markdown_v2()}\!
                            Я бот задающий интересные вопросы
                            Выберите дальнейшее действие\.''')

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_markdown_v2(text=greetings,
                                     reply_markup=markup)
    return QUESTION


def ask_question(update: Update, context: CallbackContext, redis_client):
    print(redis_client.get('a'))
    quiz_question = fetch_random_questions()
    question = quiz_question[0]
    answer = quiz_question[1].split('\n')[1].split('.')[0]
    print(answer)
    chat_id = update.effective_message.chat_id

    redis_client.set(f'{chat_id}_question', json.dumps(question))
    redis_client.set(f'{chat_id}_answer', json.dumps(answer))
    # redis_client.set(f'{chat_id}_score', json.dumps(score))

    question = json.loads(redis_client.get(f'{chat_id}_question'))
    print(f'question--->{question}')
    greetings = f'Внимание вопрос: \n{question}'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(greetings, reply_markup=markup)
    return QUESTION

def check_answer(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    answer = update.effective_message.text
    answerr = json.loads(redis_client.get(f'{chat_id}_answer'))
    if answer == answerr:
        greetings = f'Вы ответили правильно!'
    else:
        greetings = f'Увы, ответ неверный. \nМожете попробовать еще раз или ' \
                    f'сдаться'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(greetings, reply_markup=markup)
    return QUESTION


def cancel(update: Update, context: CallbackContext, redis_client):
    greetings = "Игра закончилась, ваш счет 121 балл"
    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(greetings, reply_markup=markup)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    updater = Updater(os.getenv("TG_API_BOT"))

    with redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=0,
            password=os.getenv("REDIS_PASSWORD")
    ) as redis_client:

        question = partial(ask_question, redis_client=redis_client)
        answer = partial(check_answer, redis_client=redis_client)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                QUESTION: [MessageHandler(Filters.text("Новый вопрос ❔"), question),
                           MessageHandler(Filters.text & ~Filters.command, answer)],
                ANSWER: [
                    MessageHandler(Filters.text("Новый вопрос ❔"), question),
                    MessageHandler(Filters.text & ~Filters.command, answer)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher = updater.dispatcher
        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()