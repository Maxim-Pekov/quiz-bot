import logging
import os
from dotenv import load_dotenv
from textwrap import dedent

from telegram import ReplyKeyboardMarkup
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    updater = Updater(os.getenv("TG_API_BOT"))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()