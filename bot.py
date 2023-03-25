import json
import logging
import os
import re
import redis

from functools import partial
from dotenv import load_dotenv
from main import fetch_random_questions

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


QUESTIONS, ANSWERS = 1, 2


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    greetings = f'Приветствую! \nЯ бот задающий ' \
                f'интересные вопросы. \nНу что поиграем? 🎲.'

    message_keyboard = [["Новый вопрос ❔"],
                        ['Мой счет ✍️']]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    context.user_data["score"] = 0
    update.message.reply_text(text=greetings, reply_markup=markup)
    return QUESTIONS


def ask_question(update: Update, context: CallbackContext, redis_client):
    quiz_question = fetch_random_questions()
    question = re.sub(r'Вопрос \d+:\s+', '', quiz_question[0])
    answer = re.sub(r'Ответ:\s+', '', quiz_question[1])
    print(answer)
    chat_id = update.effective_message.chat_id

    redis_client.set(f'{chat_id}_question', json.dumps(question))
    redis_client.set(f'{chat_id}_answer', json.dumps(answer))

    question = json.loads(redis_client.get(f'{chat_id}_question'))

    print(f'question--->{question}')
    greetings = f'Внимание вопрос: \n\n{question}'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(greetings, reply_markup=markup)
    return ANSWERS


def check_answer(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    user_answer = update.effective_message.text.lower()
    answer = json.loads(redis_client.get(f'{chat_id}_answer')).split('.')[0].lower()
    if user_answer == answer:
        context.user_data["score"] += 1
        total_score = json.loads(redis_client.get(f'{chat_id}_score'))
        redis_client.set(f'{chat_id}_score', total_score + 1)
        greetings = f'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        greetings = f'Неправильно… Попробуешь ещё раз?'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(greetings, reply_markup=markup)
    return ANSWERS


def show_answer(update: Update, context: CallbackContext, redis_client):
    score = context.user_data["score"]
    chat_id = update.effective_message.chat_id
    answer = json.loads(redis_client.get(f'{chat_id}_answer'))
    greetings = f"Правильный ответ \n\n{answer}, \n\nВаш счет текущей партии" \
                f" {score} балл(а/ов)"
    update.message.reply_text(greetings)
    ask_question(update, context, redis_client)


def check_score(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    score = context.user_data["score"]
    total_score = json.loads(redis_client.get(f'{chat_id}_score'))
    greetings = f"Ваш счет текущей партии {score} балл(а/ов) \n\n" \
                f"Ваш общий итоговый счет {total_score} балл(а/ов)"
    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text(greetings, reply_markup=markup)
    return QUESTIONS


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Прощай! Я надеюсь мы встретимся снова в другой раз.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


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
        fail = partial(show_answer, redis_client=redis_client)
        score = partial(check_score, redis_client=redis_client)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                QUESTIONS: [
                    MessageHandler(Filters.text("Новый вопрос ❔"), question),
                    MessageHandler(Filters.text("Мой счет ✍️"), score),
                ],
                ANSWERS: [
                    MessageHandler(Filters.text("Новый вопрос ❔"), question),
                    MessageHandler(Filters.text("Сдаться ❌"), fail),
                    MessageHandler(Filters.text("Мой счет ✍️"), score),
                    MessageHandler(Filters.text & ~Filters.command, answer)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher = updater.dispatcher
        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
