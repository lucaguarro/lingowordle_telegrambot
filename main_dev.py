import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Defaults
import commands as c
import logging
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('API_KEY_DEV')
PORT = int(os.getenv('PORT', default=8443))
logging.getLogger().setLevel(logging.INFO)

def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    defaults = Defaults(parse_mode='MarkdownV2')
    updater = Updater(API_KEY, use_context=True, defaults=defaults)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", c.start_command))
    dp.add_handler(CallbackQueryHandler(c.button))
    dp.add_handler(CommandHandler("guess", c.guess_command))
    dp.add_handler(CommandHandler("status", c.status_command))
    dp.add_handler(CommandHandler("addlang", c.add_language_command))
    dp.add_handler(CommandHandler("dellang", c.del_language_command))
    dp.add_handler(CommandHandler("seelangs", c.see_languages_command))
    dp.add_handler(CommandHandler("help", c.help_command))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()