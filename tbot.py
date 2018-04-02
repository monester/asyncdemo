import os
from telegram.ext import Updater

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
updater = Updater(token=TELEGRAM_TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    print(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

