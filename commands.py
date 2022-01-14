from bs4 import BeautifulSoup
import enchant
from collections import Counter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

d = enchant.Dict("en_US")

def start_command(update, context):
    # context.chat_data['test'] = 1

    soup = BeautifulSoup(update.message.text_html, features="html.parser")
    tag=soup.find("span", {"class": "tg-spoiler"})

    if tag is None:
        update.message.reply_text('The word must be in spoiler text so the other players can\'t see it\!')
        return

    potential_lingo_word = tag.string.upper()
    context.chat_data['potential_lingo_word'] = potential_lingo_word
    lingo_word = context.chat_data.get('lingo_word')

    if len(potential_lingo_word) != 5:
        update.message.reply_text('Lingo word must be 5 characters long\. No less and no more\.\nGame word was not set\.')
    elif not d.check(potential_lingo_word):
        update.message.reply_text('Word was not in the english dictionary\. Please make sure you spelled it correctly\.')
    else:
        guesses = context.chat_data.get('guesses')
        if lingo_word and (not guesses or (len(guesses) and guesses[-1] != lingo_word)):
            keyboard = [
                [
                    InlineKeyboardButton("Yeah Dude", callback_data='1'),
                    InlineKeyboardButton("Neh", callback_data='2'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('You guys haven\'t finished the last game\. Are you sure you want to start a new one:', reply_markup=reply_markup)
        else:
            context.chat_data['lingo_word'] = context.chat_data['potential_lingo_word']
            context.chat_data['potential_lingo_word'] = None
            context.chat_data['guesses'] = None
            update.message.reply_text('Game has started\. Waiting for guesses from players\.')

def button(update, context):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    if query.data == '1':
        context.chat_data['lingo_word'] = context.chat_data['potential_lingo_word']
        query.message.reply_text('Game has started\. Waiting for guesses from players\.')

    context.chat_data['potential_lingo_word'] = None

def validate_guess(lingo_word, guess):
    correctness = [-1,-1,-1,-1,-1]
    counter = Counter(lingo_word)
    for i in range(len(guess)):
        if guess[i] == lingo_word[i]:
            correctness[i] = 2
            counter[guess[i]] -= 1
        elif counter[guess[i]]:
            correctness[i] = 1
            counter[guess[i]] -= 1
        else:
            correctness[i] = 0
    
    return correctness

def gen_colors(correctness):
    colors = ''
    for i in range(len(correctness)):
        val = correctness[i]
        if val == 2:
            colors += '🟩'
        elif val == 1:
            colors += '🟨'
        elif val == 0:
            colors += '🟥'
    return colors

def gen_text(correctness, guess):
    str_res = ''
    for i in range(len(correctness)):
        val = correctness[i]
        if val == 2:
            str_res += '*' + guess[i] + '*'
        elif val == 1:
            str_res += '_' + guess[i] + '_'
        elif val == 0:
            str_res += '~' + guess[i] + '~'
        if i % 2 == 0:
            str_res += ' ' * 2
        else:
            str_res += ' ' * 3
    return str_res

def generate_guess_response(correctness, guess):
    colors = '' + gen_colors(correctness)
    str_res = ' ' + gen_text(correctness, guess)
    full_res = colors + '\n' + str_res + '\n' + colors
    return full_res

def generate_win_response(str_res, guesses):
    num_guesses = len(guesses)
    if num_guesses > 1:
        win_res = "YOU GOT IT RIGHT BUDDY AND IT ONLY TOOK YOU " + str(num_guesses) + " TRIES"
    elif num_guesses == 1:
        win_res = "ONE AND DONE BABY ONE AND DONE"
    return str_res + '\n' + win_res

def generate_incorrect_response(str_res, guesses):
    num_guesses = len(guesses)
    inc_res = "GUESS \#" + str(num_guesses)
    return inc_res + '\n' + str_res

def guess_command(update, context):
    # context.chat_data['test'] += 1
    # print(context.chat_data['test'])
    lingo_word = context.chat_data.get('lingo_word')
    guesses = context.chat_data.get('guesses')
    if not lingo_word:
        update.message.reply_text('No word has been set\. Please have a player set a word before making guesses\.')
        return
    elif guesses and guesses[-1] == lingo_word:
        update.message.reply_text('You guys already got this word bruh\. Start a new word with the \'start\' command or see your former guesses with \'status\'\.')
        return

    guess = context.args[0].upper()

    if guess is None:
        update.message.reply_text('Please guess a 5 letter word\.')
        return
    
    if len(guess) != 5:
        update.message.reply_text('Your word was not 5 letters\.')
    elif not d.check(guess):
        update.message.reply_text('Word was not in the english dictionary\. Please make sure you spelled it correctly\.')
    else:
        if not context.chat_data.get('guesses'):
            context.chat_data['guesses'] = [guess]
        else:
            context.chat_data['guesses'].append(guess)

        lingo_word = context.chat_data.get('lingo_word')
        correctness = validate_guess(lingo_word, guess)
        str_res = generate_guess_response(correctness, guess)

        if guess == lingo_word:
            str_res = generate_win_response(str_res, context.chat_data.get('guesses'))
        else:
            str_res = generate_incorrect_response(str_res, context.chat_data.get('guesses'))
        update.message.reply_text(str_res+'\n\n')
    
def status_command(update, context):
    if context.chat_data.get('guesses'):
        all_colors = []
        guesses = context.chat_data.get('guesses')
        for guess in guesses:
            lingo_word = context.chat_data.get('lingo_word')
            correctness = validate_guess(lingo_word, guess)
            colors = gen_colors(correctness)
            all_colors.append(colors)

        colors_and_guesses=["{}{}".format(a_, b_) for a_, b_ in zip(all_colors, guesses)]
        all_colors_text = '\n'.join(colors_and_guesses)
        update.message.reply_text(all_colors_text)

def help_command(update, context):
    update.message.reply_text(
'''
/start \[word\] \- \[word\] must be a 5 letter word stylized as spoiler text
/guess \[word\] \- \[word\] must be a 5 letter word
/status \- outputs all guesses made so far as well as their results'''
    )
