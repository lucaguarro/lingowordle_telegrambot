def start_command(update, context):
    update.message.reply_text(
'''
/start \[word\] \- \[word\] must be a 5 letter word stylized as spoiler text
/guess \[word\] \- \[word\] must be a 5 letter word
/status \- outputs all guesses made so far as well as their results'''
    )

def guess_command(update, context):
    update.message.reply_text(
'''
/start \[word\] \- \[word\] must be a 5 letter word stylized as spoiler text
/guess \[word\] \- \[word\] must be a 5 letter word
/status \- outputs all guesses made so far as well as their results'''
    )
    
def status_command(update, context):
    update.message.reply_text(
'''
/start \[word\] \- \[word\] must be a 5 letter word stylized as spoiler text
/guess \[word\] \- \[word\] must be a 5 letter word
/status \- outputs all guesses made so far as well as their results'''
    )

def help_command(update, context):
    update.message.reply_text(
'''
/start \[word\] \- \[word\] must be a 5 letter word stylized as spoiler text
/guess \[word\] \- \[word\] must be a 5 letter word
/status \- outputs all guesses made so far as well as their results'''
    )
