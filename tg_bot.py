import json
import logging
import os
import random
import redis

from functools import partial
from time import sleep
from dotenv import load_dotenv
from logs_handler import TelegramLogsHandler
from fetch_questions import fetch_questions, get_invisible_answer

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler


logger = logging.getLogger(__name__)
exception_logger = logging.getLogger('exception_logger')

QUESTIONS, ANSWERS = 1, 2


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    greetings = 'Приветствую! \nЯ бот задающий интересные вопросы. ' \
                '\nНу что поиграем? 🎲.'

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


def ask_question(update: Update, context: CallbackContext, redis_client, quiz_questions):
    quiz_question = random.choice(quiz_questions)

    chat_id = update.effective_message.chat_id

    redis_client.set(f'{chat_id}_question', json.dumps(quiz_question))

    logger.info(f'question--->{quiz_question[0]}, \nanswer--->{quiz_question[1]}')

    invisible_answer = get_invisible_answer(quiz_question[1])
    bot_message = f'Внимание вопрос: \n\n{quiz_question[0]}\n\n ' \
                  f'Ответ: {invisible_answer}'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(bot_message, reply_markup=markup)
    return ANSWERS


def show_clue(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id

    quiz_question = json.loads(redis_client.get(f'{chat_id}_question'))

    logger.info(f'question--->{quiz_question[0]}, \nanswer--->{quiz_question[1]}')

    invisible_answer = get_invisible_answer(quiz_question[1],
                                            redis_client,
                                            chat_id,
                                            random_character=True)
    # redis_client.set(f'{chat_id}_clue', json.dumps(characters))
    bot_message = f'Внимание вопрос: \n\n{quiz_question[0]}\n\n ' \
                  f'Ответ: {invisible_answer}'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(bot_message, reply_markup=markup)
    return ANSWERS


def check_answer(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    user_answer = update.effective_message.text.lower()
    answer = json.loads(redis_client.get(f'{chat_id}_question'))[1]
    lower_answer = answer.lower()
    if user_answer == lower_answer:
        context.user_data["score"] += 1

        total_score = json.loads(redis_client.get(f'{chat_id}_score'))
        redis_client.set(f'{chat_id}_score', total_score + 1)
        bot_answer = 'Правильно! Поздравляю! ' \
                     'Для следующего вопроса нажми «Новый вопрос»'
    else:
        bot_answer = 'Неправильно… Попробуешь ещё раз?'

    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(bot_answer, reply_markup=markup)
    return ANSWERS


def show_answer(update: Update, context: CallbackContext, redis_client, quiz_questions):
    score = context.user_data["score"]
    chat_id = update.effective_message.chat_id
    answer = json.loads(redis_client.get(f'{chat_id}_question'))[1]
    bot_answer = f'Правильный ответ \n\n{answer},\n\nВаш счет текущей партии' \
                 f' {score} балл(а/ов)'
    update.message.reply_text(bot_answer)
    ask_question(update, context, redis_client, quiz_questions)


def check_score(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    score = context.user_data["score"]
    if redis_client.get(f'{chat_id}_score') == None:
        redis_client.set(f'{chat_id}_score', 0)
    total_score = json.loads(redis_client.get(f'{chat_id}_score'))
    bot_answer = f"Ваш счет текущей партии {score} балл(а/ов) \n\n" \
                 f"Ваш общий итоговый счет {total_score} балл(а/ов)"
    message_keyboard = [["Новый вопрос ❔", "Сдаться ❌"],
                        ['Мой счет ✍️']]
    markup = ReplyKeyboardMarkup(
        message_keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text(bot_answer, reply_markup=markup)
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
    chat_id = os.getenv('TG_CHAT_ID')
    api_tg_token = os.getenv("TG_API_BOT")
    questions_dir = os.getenv('QUESTIONS_DIR')

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                               '%(message)s', datefmt='%d-%m-%Y %I:%M:%S %p',
                        level=logging.INFO)

    quiz_questions = fetch_questions(questions_dir)
    exception_logger.setLevel(logging.ERROR)
    exception_logger.addHandler(TelegramLogsHandler(api_tg_token, chat_id))

    with redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=0,
    ) as redis_client:

        question = partial(
            ask_question,
            redis_client=redis_client,
            quiz_questions=quiz_questions
        )
        answer = partial(check_answer, redis_client=redis_client)
        fail = partial(
            show_answer,
            redis_client=redis_client,
            quiz_questions=quiz_questions
        )
        score = partial(check_score, redis_client=redis_client)
        clue = partial(show_clue, redis_client=redis_client)

        updater = Updater(api_tg_token)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                QUESTIONS: [
                    MessageHandler(
                        Filters.text("Новый вопрос ❔"), question
                    ),
                    MessageHandler(Filters.text("Мой счет ✍️"), score),
                ],
                ANSWERS: [
                    MessageHandler(
                        Filters.text("Новый вопрос ❔"), question
                    ),
                    MessageHandler(Filters.text("Сдаться ❌"), fail),
                    MessageHandler(Filters.text("Мой счет ✍️"), score),
                    MessageHandler(Filters.text("Подсказка"), clue),
                    MessageHandler(
                        Filters.text & ~Filters.command, answer
                    )
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
