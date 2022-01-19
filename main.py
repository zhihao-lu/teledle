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

from telegram import InlineKeyboardMarkup, Update, ReplyKeyboardRemove, InlineKeyboardButton, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

WORD = "EMILY"

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [[InlineKeyboardButton("Yes", callback_data='Yes')]]
markup = InlineKeyboardMarkup(reply_keyboard)


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(

        "Play Zhihao-dle",
        reply_markup=markup
    )

    return "start"


def start_game(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["guess_string"] = "Guess a 5 letter word\. Correct characters are in *bold*, correct characters "\
                                        "in the wrong position are in _italics_\. Wrong characters appear at the side\." \
                                        " \n \_ \_ \_ \_ \_ \n "
    context.user_data["remaining_chars"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Send the key to the user
    query.edit_message_text(context.user_data["guess_string"], parse_mode=ParseMode.MARKDOWN_V2)
    return "guess"


def generate_guess_string(answer, guess, context):
    answer = answer.upper()
    guess = guess.upper()

    correct = ''
    side = ''
    for idx, char in enumerate(guess):
        if char == answer[idx]:
            correct += f"*{char}*  "
        elif char in answer:
            correct += f"_{char}_ "
        else:
            correct += "\_ "
            side += f"{char} "
        context.user_data["remaining_chars"] = context.user_data["remaining_chars"].replace(char, "")
    out = correct + "\| " + side + "\n"

    if answer == guess:
        out += "Congrats you won!"

    return out, answer == guess


def verify_guess(update, context):
    name = update.message.from_user.first_name
    tele = update.message.from_user.username
    guess = update.message.text
    guess_string, has_won = generate_guess_string(WORD, guess, context)

    context.user_data["guess_string"] = context.user_data["guess_string"] + guess_string

    if has_won:
        keyboard = [
            [InlineKeyboardButton("Record another", callback_data='track_exercise')],
            [InlineKeyboardButton("Back", callback_data='return_menu')]
        ]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(context.user_data["guess_string"])  # , reply_markup=reply_markup)
        return "win"
    update.message.reply_text(context.user_data["guess_string"] + "\n\n" + \
                              "Characters remaining: \n" + \
                              " ".join(context.user_data["remaining_chars"]),
                              parse_mode=ParseMode.MARKDOWN_V2)  # , reply_markup=reply_markup)
    return "guess"
    if "win":
        return "win"
    elif "too many guesses":
        return "lose"
    else:
        return "guess"


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

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            "start": [
                CallbackQueryHandler(start_game, pattern="Yes"),
            ],
            "guess": [
                MessageHandler(
                    Filters.all, verify_guess
                )
            ],
            "win": [

            ]

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), start)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
