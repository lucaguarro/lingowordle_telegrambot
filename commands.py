from bs4 import BeautifulSoup
from collections import Counter
from datetime import date
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

with open("./assets/dictionaries/english.txt", "r") as f:
    d_en = {line.strip() for line in f}

with open("./assets/dictionaries/italian.txt", "r") as f:
    d_it = {line.strip() for line in f}

dict_set = {'en': d_en, 'it': d_it}

def add_lang_to_chat(lang, context):
    if context.chat_data.get('languages') and lang in context.chat_data.get('languages'):
        return -1
    if not context.chat_data.get('languages'):
        context.chat_data['languages'] = [lang]
    else:
        context.chat_data['languages'].append(lang)
    return 1

def add_language_command(update, context):
    lingo_word = context.chat_data.get('lingo_word')
    guesses = context.chat_data.get('guesses')
    if lingo_word and (not guesses or (len(guesses) and guesses[-1] != lingo_word)):
        update.message.reply_text('You can\'t modify the languages in the middle of a game\.')
    else:
        lang = context.args[0].upper()

        if lang not in ['ENGLISH', 'ITALIAN']:
            update.message.reply_text('That language is not supported\. Italian and English are supported\.')
            return
        elif lang == 'ENGLISH':
            status = add_lang_to_chat('en', context)
        elif lang == 'ITALIAN':
            status = add_lang_to_chat('it', context)

        if status == -1:
            update.message.reply_text('This language was already added\.')
        else:
            update.message.reply_text(lang + ' WAS ADDED\.')
    
def del_lang_from_chat(lang, context):
    if context.chat_data.get('languages') and lang in context.chat_data.get('languages'):
        context.chat_data.get('languages').remove(lang)
        return 1
    else:
        return -1

def del_language_command(update, context):
    lingo_word = context.chat_data.get('lingo_word')
    guesses = context.chat_data.get('guesses')
    if lingo_word and (not guesses or (len(guesses) and guesses[-1] != lingo_word)):
        update.message.reply_text('You can\'t modify the languages in the middle of a game\.')
    else:
        lang = context.args[0].upper()
        if lang == 'ENGLISH':
            status = del_lang_from_chat('en', context)
        elif lang == 'ITALIAN':
            status = del_lang_from_chat('it', context)
        if status == 1:
            update.message.reply_text(lang + ' DELETED')
        else:
            update.message.reply_text('That language was never added\.')

def see_languages_command(update, context):
    str_res = 'You are playing with the following languages:  '
    if context.chat_data.get('languages'):
        for lang in context.chat_data.get('languages'):
            str_res += lang + ', '
        str_res = str_res[0:len(str_res)-2]
    update.message.reply_text(str_res)

def start_command(update, context):
    if not context.chat_data.get('languages'):
        context.chat_data['languages'] = ['en']

    soup = BeautifulSoup(update.message.text_html, features="html.parser")
    tag=soup.find("span", {"class": "tg-spoiler"})

    if tag is None:
        update.message.reply_text('The word must be in spoiler text so the other players can\'t see it\!')
        return

    potential_lingo_word = tag.string.upper()
    context.chat_data['potential_lingo_word'] = potential_lingo_word
    lingo_word = context.chat_data.get('lingo_word')

    if len(potential_lingo_word) < 4 or len(potential_lingo_word) > 10:
        update.message.reply_text('Lingo word must be between 4 and 10 characters long\. \n ❌ Game word was not set\. ❌')
    elif not any([potential_lingo_word.lower() in dict_set[lang] for lang in context.chat_data['languages']]): #d.check(potential_lingo_word):
        update.message.reply_text('Word was not in the following active languages: '+ ', '.join(context.chat_data['languages']) + '\. Please make sure you spelled it correctly\.  \n ❌ Game word was not set\. ❌')
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
            update.message.reply_text('✅ Game has started and the word has *' + str(len(potential_lingo_word)) + '* characters\. Waiting for guesses from players\. ✅')

def button(update, context):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    if query.data == '1':
        context.chat_data['lingo_word'] = context.chat_data['potential_lingo_word']
        context.chat_data['guesses'] = None
        query.message.reply_text('✅ Game has started and the word has *' + str(len(context.chat_data['lingo_word'])) + '* characters\. Waiting for guesses from players\. ✅')
    if query.data == '2':
        query.message.reply_text('Game continues...')

    context.chat_data['potential_lingo_word'] = None

def validate_guess(lingo_word, guess):
    correctness = [-1] * len(lingo_word)
    indices_of_known = []
    counter = Counter(lingo_word)
    for i in range(len(guess)):
        if guess[i] == lingo_word[i]:
            correctness[i] = 2
            counter[guess[i]] -= 1
            indices_of_known.append(i)

    for i in range(len(guess)):
        if not correctness[i] == 2:
            if counter[guess[i]]:
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

def select_random_line_from_file(src_file, num_g, usrname):
    today = date.today()
    def random_line(afile):
        line = next(afile)
        for num, aline in enumerate(afile, 2):
            if random.randrange(num):
                continue
            line = aline
        return line
    with open(src_file, 'r') as file:
        myline = random_line(file)
    day = today.strftime("%B %d, %Y")
    return myline.format(username=usrname, num_guesses=num_g, date=day)


def generate_win_response(str_res, guesses, username):
    num_guesses = len(guesses)

    if num_guesses == 1:
        source_file = './assets/responses/wins/one.txt'
    elif num_guesses > 1 and num_guesses <= 4:
        source_file = './assets/responses/wins/two_four.txt'
    elif num_guesses > 4 and num_guesses < 10:
        source_file = './assets/responses/wins/five_nine.txt'
    elif num_guesses >= 10:
        source_file = './assets/responses/wins/ten_more.txt'

    if username == 'freedomlandstudios':
        win_res = 'ROBERTI\!\!\!\! YOU ABSOLUTE ANIMAL YOU FUCKING GOT IT\, KEEP ON ROCKIN\' BUDDY\!\!'
    else:
        win_res = select_random_line_from_file(source_file, num_guesses, username)
    return str_res + '\n' + win_res

def generate_incorrect_response(str_res, guesses):
    num_guesses = len(guesses)
    inc_res = "GUESS \#" + str(num_guesses)
    return inc_res + '\n' + str_res

def guess_command(update, context):
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
        update.message.reply_text('Please guess a word between 4 and 10 characters\.')
        return
    
    if len(guess) != len(lingo_word):
        update.message.reply_text('Your word must be the length of the set word which is ' + str(len(lingo_word)))
    elif not any([guess.lower() in dict_set[lang] for lang in context.chat_data['languages']]): #not d.check(guess):
        update.message.reply_text('Word was not in the dictionary\. Please make sure you spelled it correctly\.')
    else:
        if not context.chat_data.get('guesses'):
            context.chat_data['guesses'] = [guess]
        else:
            context.chat_data['guesses'].append(guess)

        lingo_word = context.chat_data.get('lingo_word')
        correctness = validate_guess(lingo_word, guess)
        str_res = generate_guess_response(correctness, guess)

        if guess == lingo_word:
            str_res = generate_win_response(str_res, context.chat_data.get('guesses'), update.message.from_user['username'])
        else:
            str_res = generate_incorrect_response(str_res, context.chat_data.get('guesses'))
        update.message.reply_text(str_res+'\n\n')

def get_summary(guesses, correctnesses):
    # if correctnesses[i][j] == 2, then we know the letter
    known_letters = ['\_'] * len(guesses[0])
    overall_set = {}
    for i in range(len(guesses)):
        curr_set = {}
        for j in range(len(guesses[0])):
            if correctnesses[i][j]:
                if correctnesses[i][j] == 2 and known_letters[j] == '\_':
                    known_letters[j] = guesses[i][j]

                if guesses[i][j] in curr_set:
                    curr_set[guesses[i][j]] += 1
                else:
                    curr_set[guesses[i][j]] = 1

        for key in curr_set:
            if key in overall_set:
                if curr_set[key] > overall_set[key]:
                    overall_set[key] = curr_set[key]
            else:
                overall_set[key] = curr_set[key]

    for i in range(len(known_letters)):
        if known_letters[i] != '\_':
            if known_letters[i] in overall_set:
                overall_set[known_letters[i]] -= 1

    leftovers = [k for k in overall_set for i in range(overall_set[k])]
    found_res = '*So Far:  *' + ' '.join(known_letters)
    leftovers = '*Known Letters:  *' + ', '.join(leftovers)
    return '\n' + found_res + '\n' + leftovers

    
def status_command(update, context):
    if context.chat_data.get('guesses'):
        all_colors = []
        guesses = context.chat_data.get('guesses')
        lingo_word = context.chat_data.get('lingo_word')
        correctnesses = []
        for guess in guesses:
            correctness = validate_guess(lingo_word, guess)
            colors = gen_colors(correctness)
            all_colors.append(colors)
            correctnesses.append(correctness)

        summary = get_summary(guesses, correctnesses)
        colors_and_guesses=["{}{}".format(a_, b_) for a_, b_ in zip(all_colors, guesses)]
        all_colors_text = '\n'.join(colors_and_guesses)
        update.message.reply_text(all_colors_text + '\n' + summary)

def help_command(update, context):
    update.message.reply_text(
'''
/start \[word\] \- \[word\] must be a 4\-10 letter word stylized as spoiler text
/guess \[word\] \- \[word\] must be a letter word with length of that of the set word
/status \- outputs all guesses made so far as well as their results
/addlang \[language\] \- Add a language to the set of allowable words\. English and Italian supported\. If no language is set\, English will be used by default\.
/dellang \[language\] \- Delete a language to the set of allowable words\. English and Italian supported\.
/seelangs \- See all active languages'''
    )
