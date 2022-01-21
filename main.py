# !/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import os
import logging
from typing import Dict

from telegram import InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

WORD = "FLOOR"

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [[InlineKeyboardButton("Yes", callback_data='start_game')],
                  [InlineKeyboardButton("Test, don't click.", callback_data='test')]]
markup = InlineKeyboardMarkup(reply_keyboard)


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(

        "Play Zhihao-dle",
        reply_markup=markup
    )

    return "start"


def show_back_home(update, context):
    query = update.callback_query
    query.answer()

    text = "Welcome back. Play zhihao-dle"
    query.edit_message_text(text, reply_markup=markup)
    return ""


def start_game(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["num_guesses"] = 0
    context.user_data["guess_string"] = "Guess a 5 letter word\. Correct characters are in *bold*, correct characters "\
                                        "in the wrong position are in _italics_\. Wrong characters appear at the side\." \
                                        "\n \_ \_ \_ \_ \_ \n"
    context.user_data["remaining_chars"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    context.user_data["guessed_chars"] = ""


    query.edit_message_text(context.user_data["guess_string"], parse_mode=ParseMode.MARKDOWN_V2)
    return "guess"


def generate_guess_string(answer, guess, context):
    answer = answer.upper()
    guess = guess.upper()

    correct = [""] * 5
    for i in range(5):
        if guess[i] == answer[i]:
            correct[i] = f"*{guess[i]}*"
            answer = answer[:i] + "_" + answer[i + 1:]
            guess = guess[:i] + "." + guess[i + 1:]
            context.user_data["remaining_chars"] = context.user_data["remaining_chars"].replace(guess[i], "")

    for idx, val in enumerate(correct):
        if val:
            continue
        guess_char = guess[idx]
        if not val and guess_char in answer:
            correct[idx] = f"_{guess_char}_"
            answer = answer.replace(guess_char, "_", 1)
            guess = guess.replace(guess_char, ".", 1)
        else:
            correct[idx] = f"\_"
            context.user_data["guessed_chars"] += guess_char
        context.user_data["remaining_chars"] = context.user_data["remaining_chars"].replace(guess_char, "")

    out = " ".join(correct) + "\| " + " ".join(sorted(set(context.user_data["guessed_chars"]))) + "\n"

    return out, answer == guess


def valid_guess(guess):
    return len(guess) == 5


def verify_guess(update, context):
    guess = update.message.text
    name = update.message.from_user.first_name
    print(f"{name} guessed: {guess}")
    if not valid_guess(guess):
        update.message.reply_text("5 letters only!")
        return "guess"

    context.user_data["num_guesses"] = context.user_data["num_guesses"] + 1
    guess_string, has_won = generate_guess_string(WORD, guess, context)

    context.user_data["guess_string"] = context.user_data["guess_string"] + guess_string

    if has_won:
        keyboard = [
            [InlineKeyboardButton("Play again", callback_data='start_game')],
            [InlineKeyboardButton("Back", callback_data='return_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(context.user_data["guess_string"] + "\n\n" +
                                  f"**You win\! You took {context.user_data['num_guesses']} guesses\.**",
                                  parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=reply_markup)
        return "end"
    elif context.user_data["num_guesses"] > 5:
        keyboard = [
            [InlineKeyboardButton("Play again", callback_data='start_game')],
            [InlineKeyboardButton("Back", callback_data='return_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(context.user_data["guess_string"] + "\n\n" +
                                  f"\n Ran out of guesses\! The word was *{WORD}*\.",
                                  parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=reply_markup)
        return "end"
    update.message.reply_text(context.user_data["guess_string"] + "\n\n" +
                              f"Guesses remaining: *{6 - context.user_data['num_guesses']}*\.\n"
                              "Characters remaining: \n" +
                              " ".join(context.user_data["remaining_chars"]),
                              parse_mode=ParseMode.MARKDOWN_V2)  # , reply_markup=reply_markup)
    return "guess"
    if "win":
        return "win"
    elif "too many guesses":
        return "lose"
    else:
        return "guess"

reply_keyboard1 = [
        [InlineKeyboardButton('q', callback_data='q'), InlineKeyboardButton('w', callback_data='w')],
        [InlineKeyboardButton('a', callback_data='a'), InlineKeyboardButton('s', callback_data='s')],
        [InlineKeyboardButton('z', callback_data='z')],
    ]

pressed = '1'
s = "u r gay "
stack = []
def test_start(update, context):
    query = update.callback_query
    reply_keyboard = [[InlineKeyboardButton(char, callback_data=char) for char in 'qwertyuiop' if char not in pressed],
                      [InlineKeyboardButton(char, callback_data=char) for char in 'asdfghjkl' if char not in pressed],
                      [InlineKeyboardButton(char, callback_data=char) for char in 'zxcvbnm' if char not in pressed]]


    markup = InlineKeyboardMarkup(reply_keyboard)
    query.edit_message_text("u r gay ", reply_markup=markup)
    return "continue"

def test_start2(update, context):
    query = update.callback_query
    query.answer()
    text = query.data
    global pressed
    global s
    global stack
    if text == "delete" and stack:
        text = stack.pop()
        s = s.replace(text, "")
    elif text != "delete":
        stack.append(text)
        s += text
    print(stack)

    reply_keyboard = [[InlineKeyboardButton(char, callback_data=char) for char in 'qwertyuiop' if char not in stack],
                      [InlineKeyboardButton(char, callback_data=char) for char in 'asdfghjkl' if char not in stack],
                      [InlineKeyboardButton(char, callback_data=char) for char in 'zxcvbnm' if char not in stack],
                      [InlineKeyboardButton("Submit", callback_data="submit"), InlineKeyboardButton("Delete", callback_data="delete")]]


    markup = InlineKeyboardMarkup(reply_keyboard)
    query.edit_message_text(s, reply_markup=markup)
    return "continue"


def done(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ["TOKEN"])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(show_back_home, pattern="return_menu"))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CallbackQueryHandler(start, pattern="start_game")],
        states={
            "start": [
                CallbackQueryHandler(start_game, pattern="start_game"),
            ],
            "guess": [
                MessageHandler(
                    Filters.regex('.'), verify_guess
                ),
            ],
            "end": [
                CallbackQueryHandler(start_game, pattern="start_game"),
                CallbackQueryHandler(show_back_home, pattern="return_menu")
            ]

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), start)],

    )

    dispatcher.add_handler(conv_handler)

    test_conv_handler = ConversationHandler(
        entry_points=[
                      CallbackQueryHandler(test_start, pattern="test")],
        states={
            "continue": [
                CallbackQueryHandler(test_start2, pattern=".|delete")
            ],
            "guess": [
                MessageHandler(
                    Filters.all, verify_guess
                ),
            ]

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), start),
                   CommandHandler('start', start)],

    )

    dispatcher.add_handler(test_conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
