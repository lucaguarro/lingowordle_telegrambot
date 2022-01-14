import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Defaults
import commands as c

# API_KEY = os.getenv('API_KEY')
API_KEY = os.environ.get('API_KEY')
PORT = int(os.environ.get('PORT', '13978'))

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
    dp.add_handler(CommandHandler("help", c.help_command))

    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=API_KEY,
                          webhook_url='https://wordle-telegram-bot.herokuapp.com/' + API_KEY)

    updater.idle()

if __name__ == '__main__':
    main()