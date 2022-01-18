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

from telegram import InlineKeyboardMarkup, Update, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)


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
    context.user_data["guess_string"] = "Guess a 5 letter word \n _ _ _ _ _"
    # Send the key to the user
    query.edit_message_text(context.user_data["guess_string"])
    return "guess"


def verify_guess(update, context):
    name = update.message.from_user.first_name
    tele = update.message.from_user.username
    guess = update.message.text
    print(guess)

    keyboard = [
        [InlineKeyboardButton("Record another", callback_data='track_exercise')],
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"You guessed {guess}", reply_markup=reply_markup)

    if "win":
        return "win"
    elif "too many guesses":
        return "lose"
    else:
        return "guess"



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
