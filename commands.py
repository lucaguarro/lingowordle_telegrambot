from bs4 import BeautifulSoup
import enchant
from collections import Counter

# green_box_check = '\xE2\x9C\x85'
# warning_sign = '\xE2\x9A\xA0'
# no_entry = '\xE2\x9B\x94'

d = enchant.Dict("en_US")
lingo_word = None
guesses = []
all_colors = []

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


def validate_guess(guess):
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

def generate_guess_response(correctness, guess):
    global all_colors
    colors = ''
    str_res = '  '
    for i in range(len(correctness)):
        val = correctness[i]
        if val == 2:
            colors += '🟩'
            str_res += '*' + guess[i] + '*'
        elif val == 1:
            colors += '🟨'
            str_res += '_' + guess[i] + '_'
        elif val == 0:
            colors += '🟥'
            str_res += '~' + guess[i] + '~'
        if i % 2 == 0:
            str_res += ' ' * 4
        else:
            str_res += ' ' * 5
    
    all_colors.append(colors)
    
    full_res = colors + '\n' + str_res + '\n' + colors
    return full_res

def generate_win_response():
    num_guesses = len(guesses)
    win_res = "YOU GOT IT RIGHT BUDDY AND IT ONLY TOOK YOU " + str(num_guesses) + " TRIES"
    return win_res

def guess_command(update, context):
    print("CONTEXT", context)

    if not lingo_word:
        update.message.reply_text('No word has been set\. Please have a player set a word before making guesses\.')
        return
    elif len(guesses) and guesses[-1] == lingo_word:
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
        global guesses
        guesses.append(guess)
        correctness = validate_guess(guess)
        str_res = generate_guess_response(correctness, guess)

        if guess == lingo_word:
            generate_win_response()
        else:
            generate_incorrect_response()

        update.message.reply_text(str_res+'\n\n')
    
def status_command(update, context):
    colors_and_guesses=["{}{}".format(a_, b_) for a_, b_ in zip(all_colors, guesses)]
    all_colors_text = '\n'.join(colors_and_guesses)

def help_command(update, context):
    update.message.reply_text(
        '''
        /start [word] - [word] must be a 5 letter word stylized as spoiler text\n
        /guess [word] - [word] must be a 5 letter word
        /status - outputs all guesses made so far as well as their results
        '''
    )
