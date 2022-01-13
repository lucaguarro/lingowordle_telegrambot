import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Defaults
from telegram import ParseMode, Update, ForceReply
import logging
from bs4 import BeautifulSoup
import enchant
from collections import Counter

import responses as r

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

load_dotenv()
API_KEY = os.getenv('API_KEY')

d = enchant.Dict("en_US")
lingo_word = None

def start_command(update, context):

    soup = BeautifulSoup(update.message.text_html)
    tag=soup.find("span", {"class": "tg-spoiler"})

    if tag is None:
        update.message.reply_text('The word must be in spoiler text so the other players can\'t see it\!')
        return

    global lingo_word
    lingo_word = tag.string.upper()
    print("lingo_word", lingo_word)
    print("tag", tag)

    if len(lingo_word) != 5:
        update.message.reply_text('Lingo word must be 5 characters long\. No less and no more\.\nGame word was not set\.')
    elif not d.check(lingo_word):
        update.message.reply_text('Word was not in the english dictionary\. Please make sure you spelled it correctly\.')
    else:
        update.message.reply_text('Game has started\. Waiting for guesses from players\.')

def guess_command(update, context):
    # soup = BeautifulSoup(update.message.text_html)
    # print("to_parse", update.message.text_html)
    # tag=soup.find("span")
    print("***", context.args)
    correctness = [-1,-1,-1,-1,-1]

    print("the lingo word", lingo_word)
    if not lingo_word:
        update.message.reply_text('No word has been set\. Please have a player set a word before making guesses\.')

    guess = context.args[0].upper()

    if guess is None:
        update.message.reply_text('Please guess a 5 letter word\.')
        return

    counter = Counter(lingo_word)
    if len(guess) != 5:
        update.message.reply_text('Your word was not 5 letters\.')
    elif not d.check(guess):
        update.message.reply_text('Word was not in the english dictionary\. Please make sure you spelled it correctly\.')
    else:
        not_complete = []
        for i in range(len(guess)):
            if guess[i] == lingo_word[i]:
                correctness[i] = 2
                counter[guess[i]] -= 1
            elif counter[guess[i]]:
                correctness[i] = 1
                counter[guess[i]] -= 1
            else:
                correctness[i] = 0

        str_res = ''
        for i in range(len(correctness)):
            val = correctness[i]
            if val == 2:
                str_res += '*' + guess[i] + '*'
            elif val == 1:
                str_res += '`' + guess[i] + '`'
            elif val == 0:
                str_res += '~' + guess[i] + '~'

        update.message.reply_text(str_res)



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
    dp.add_handler(CommandHandler("guess", guess_command)) # , Filters.entity('spoiler')
    dp.add_handler(CommandHandler("help", start_command))

    # dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)
    updater.start_polling(0)
    updater.idle()

main()