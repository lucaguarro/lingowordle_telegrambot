import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Defaults
from telegram import ParseMode, Update, ForceReply
import logging
from bs4 import BeautifulSoup
# from html.parser import HTMLParser

import responses as r

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

load_dotenv()
API_KEY = os.getenv('API_KEY')

lingo_word = None

def start_command(update, context):
    
    soup = BeautifulSoup(update.message.text_html)
    tag=soup.find("span", {"class": "tg-spoiler"})
    lingo_word = tag.string
    print("******", lingo_word)

    print("what is the length", len(lingo_word))
    if len(lingo_word) != 5:
        update.message.reply_text('Lingo word must be 5 characters long\. No less and no more\.')
    else:
        update.message.reply_text('Game has started\. Waiting for guesses from players\.')
    # update.message.reply_markdown_v2(
    #     fr'Hi {user.mention_markdown_v2()}\!',
    #     reply_markup=ForceReply(selective=True),
    # )
    # update.message.reply_text('Type something random!')

def help_command(update, context):
    update.message.reply_text('Cant help you bruh')

def handle_message(update, context):
    text = str(update.message.text).lower()
    response = r.sample_responses(text)

    update.message.reply_text(response)

def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    defaults = Defaults(parse_mode='MarkdownV2')

    updater = Updater(API_KEY, use_context=True, defaults=defaults)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command)) # , Filters.entity('spoiler')
    dp.add_handler(CommandHandler("help", start_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)
    updater.start_polling(0)
    updater.idle()

main()