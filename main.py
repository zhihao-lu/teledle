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
from functools import partial
from words import WORDS, VALID_GUESSES
import random

my_words = []
ZHIHAO_WORD = ""
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [[InlineKeyboardButton("Yes", callback_data='start_game')],
                  # [InlineKeyboardButton("Test, don't click.", callback_data='test')],
                  [InlineKeyboardButton("Give me a word to play", callback_data='give')]]
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
    return ConversationHandler.END


def cancel(update, context):
    # context.update_queue.append(update)
    return ConversationHandler.END


def start_game(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["num_guesses"] = 0
    context.user_data["guess_string"] = "Guess a 5 letter word\. Correct characters are in *bold*, correct characters " \
                                        "in the wrong position are in _italics_\. Wrong characters appear at the side\." \
                                        "\n\_ \_ \_ \_ \_ \n"
    context.user_data["remaining_chars"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    context.user_data["guessed_chars"] = ""
    context.user_data["current_word"] = random.choice(WORDS)

    query.edit_message_text(context.user_data["guess_string"], parse_mode=ParseMode.MARKDOWN_V2)
    return "guess"


def generate_guess_string(answer, guess, context):
    answer = answer.upper()
    guess = guess.upper()
    answer_copy, guess_copy = answer, guess
    correct = [""] * 5
    for i in range(5):
        if guess[i] == answer[i]:
            correct[i] = f"*{guess[i]}*"
            context.user_data["remaining_chars"] = context.user_data["remaining_chars"].replace(guess[i], "")
            answer = answer[:i] + "_" + answer[i + 1:]
            guess = guess[:i] + "." + guess[i + 1:]


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

    return out, answer_copy == guess_copy


def valid_guess(guess):
    if len(guess) != 5:
        return False, "5 letters only!"
    elif guess.lower() not in VALID_GUESSES:
        print(guess.lower())
        return False, "Real words only!"
    # clean weird characters like $&#^@

    return True, ""


def verify_guess(update, context, myself=False):
    guess = update.message.text
    name = update.message.from_user.first_name
    print(f"{name} guessed: {guess}")

    valid, message = valid_guess(guess)
    if not valid:
        update.message.reply_text(message)
        return "guess"
    if myself:
        name, id, word = ZHIHAO_WORD
        context.bot.send_message(chat_id=id, text=f"Zhihao guessed {guess}.")
    else:
        word = context.user_data["current_word"]

    context.user_data["num_guesses"] = context.user_data["num_guesses"] + 1
    guess_string, has_won = generate_guess_string(word, guess, context)

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
        if myself:
            context.bot.send_message(chat_id=id, text=f"Zhihao has guessed your word {word}!")
        return ConversationHandler.END
    elif context.user_data["num_guesses"] > 5:
        keyboard = [
            [InlineKeyboardButton("Play again", callback_data='start_game')],
            [InlineKeyboardButton("Back", callback_data='return_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(context.user_data["guess_string"] + "\n\n" +
                                  f"\n Ran out of guesses\! The word was *{word}*\.",
                                  parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=reply_markup)
        if myself:
            context.bot.send_message(chat_id=id, text=f"Zhihao has guessed ran out of guesses while trying to guess "
                                                      f"your word {word}.")
        return ConversationHandler.END
    update.message.reply_text(context.user_data["guess_string"] + "\n\n" +
                              f"Guesses remaining: *{6 - context.user_data['num_guesses']}*\.\n"
                              "Characters remaining: \n" +
                              " ".join(context.user_data["remaining_chars"]),
                              parse_mode=ParseMode.MARKDOWN_V2)  # , reply_markup=reply_markup)
    return "guess"


def ask_for_word(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Submit a 5 letter word for me to guess.", reply_markup=reply_markup
    )

    return "given"


def save_word(update, context):
    word = update.message.text
    tele = update.message.from_user.username
    id = update.message.from_user.id
    if not valid_guess(word):
        update.message.reply_text("5 letters only!")
        return "given"

    global my_words
    my_words.append((tele, id, word))
    print(f"{tele} has submitted a word.")

    keyboard = [
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Submitted {word}.", reply_markup=reply_markup)
    return ConversationHandler.END


def zhihao_play(update, context):
    global my_words
    if not my_words:
        keyboard = [
            [InlineKeyboardButton("Back", callback_data='return_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"Submitted", reply_markup=reply_markup)
        return "end"
    context.user_data["num_guesses"] = 0
    context.user_data["guess_string"] = "Guess a 5 letter word\. Correct characters are in *bold*, correct characters " \
                                        "in the wrong position are in _italics_\. Wrong characters appear at the side\." \
                                        "\n\_ \_ \_ \_ \_ \n"
    context.user_data["remaining_chars"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    context.user_data["guessed_chars"] = ""
    update.message.reply_text(context.user_data["guess_string"], parse_mode=ParseMode.MARKDOWN_V2)
    global ZHIHAO_WORD
    ZHIHAO_WORD = my_words.pop(0)
    print(f"You are guessing a word from {ZHIHAO_WORD[0]}")
    context.bot.send_message(chat_id=ZHIHAO_WORD[1], text=f"Zhihao has started guessing your word {ZHIHAO_WORD[2]}")

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
                      [InlineKeyboardButton("Submit", callback_data="submit"),
                       InlineKeyboardButton("Delete", callback_data="delete")]]

    markup = InlineKeyboardMarkup(reply_keyboard)
    query.edit_message_text(s, reply_markup=markup)
    return "continue"


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ["TOKEN"])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(show_back_home, pattern="return_menu"), 1)
    dispatcher.add_handler(CommandHandler("start", start), 1)
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_game, pattern="start_game")],
        states={
            "start": [
                CallbackQueryHandler(start_game, pattern="start_game"),
            ],
            "guess": [
                MessageHandler(
                    Filters.text & ~Filters.command, verify_guess
                ),
            ],
            "end": [
                CallbackQueryHandler(start_game, pattern="start_game"),
                CallbackQueryHandler(show_back_home, pattern="return_menu")
            ]

        },
        fallbacks=[MessageHandler(Filters.command, cancel)],

    )

    submit_word_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_for_word, pattern="give")],
        states={
            "given": [
                MessageHandler(Filters.all, save_word),
            ]

        },
        fallbacks=[MessageHandler(Filters.command, cancel)],

    )

    zhihao_handler = ConversationHandler(
        entry_points=[CommandHandler("zhihao", zhihao_play)],
        states={
            "given": [
                MessageHandler(Filters.all, save_word),
            ],
            "guess": [
                MessageHandler(
                    Filters.regex('.'), partial(verify_guess, myself=True)
                ),
            ],
            "end": [
                CallbackQueryHandler(show_back_home, pattern="return_menu")
            ]

        },
        fallbacks=[MessageHandler(Filters.command, cancel)],

    )
    dispatcher.add_handler(zhihao_handler, 2)
    dispatcher.add_handler(conv_handler, 2)
    dispatcher.add_handler(submit_word_handler, 2)

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
        fallbacks=[MessageHandler(Filters.command, cancel)]

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
