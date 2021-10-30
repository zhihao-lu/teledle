# TO DO
# multiple people can use at once
# admin mode

import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, \
    ConversationHandler
from db import Database
from functools import partial

db = Database()
db.create_tables()

keyboard = [
    [InlineKeyboardButton("Track Exercise", callback_data='track_exercise')],
    [InlineKeyboardButton("Retrieve", callback_data='retrieve')],
]
main_keyboard = InlineKeyboardMarkup(keyboard)


def start(update: Update, context):
    update.message.reply_text('Please select one of the options:', reply_markup=main_keyboard)


def show_back_home(update, context):
    query = update.callback_query
    query.answer()

    text = "Welcome back home! Please select one of the options:"
    query.edit_message_text(text, reply_markup=main_keyboard)

    return ConversationHandler.END


def log_exercise(update, context, exercise=""):
    user = update.message.from_user.first_name
    tele_id = update.message.from_user.username
    score = update.message.text

    keyboard = [
        [InlineKeyboardButton("Record another", callback_data='track_exercise')],
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if exercise == "R":
        try:
            score = float(score)
            if score < 0:
                raise ValueError
            db.insert_entry(tele_id, exercise, score)
            update.message.reply_text(f"Success! Recorded {score} km for {user}.", reply_markup=reply_markup)
        except ValueError:
            update.message.reply_text(f"Input is wrong, please try again or record 0 km to exit.")
            return "LOG_" + exercise

    else:
        try:
            score = int(score)
            if score < 0:
                raise ValueError
            db.insert_entry(tele_id, exercise, score)
            update.message.reply_text(f"Success! Recorded {score} reps for {user}.", reply_markup=reply_markup)
        except ValueError:
            update.message.reply_text(f"Input is wrong, please try again or record 0 reps to exit.")
            return "LOG_" + exercise
    return ConversationHandler.END


def ask_exercise(update, context, exercise=""):
    query = update.callback_query
    query.answer()

    if exercise == "PU":
        query.edit_message_text("Pull ups selected. Please enter how many pull ups you have done:")
        return "LOG_PU"

    elif exercise == "C":
        query.edit_message_text("Core selected. Please enter how many you have done:")
        return "LOG_C"
    elif exercise == "R":
        query.edit_message_text("Run selected. Please enter how far you have ran in km (e.g. 4.6):")
        return "LOG_R"


def get_one(update, context):
    update.message.reply_text(db.get_all())


def choose_exercise(update, context):
    keyboard = [
        [InlineKeyboardButton("Pull ups", callback_data='PU'),
         InlineKeyboardButton("Core", callback_data='C'),
         InlineKeyboardButton("Run", callback_data='R')],
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text="Choose exercise: ", reply_markup=reply_markup
    )

    return "selected_exercise"


def choose_exercise_query(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Pull ups", callback_data='PU'),
         InlineKeyboardButton("Core", callback_data='C'),
         InlineKeyboardButton("Run", callback_data='R')],
        [InlineKeyboardButton("Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Choose exercise: ", reply_markup=reply_markup
    )

    return "selected_exercise"


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ['TOKEN'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(show_back_home, pattern="return_menu"))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("track_exercise", choose_exercise),
                          CallbackQueryHandler(choose_exercise_query, pattern="track_exercise")],
            states={
                "selected_exercise": [
                    CallbackQueryHandler(partial(ask_exercise, exercise="PU"), pattern='PU'),
                    CallbackQueryHandler(partial(ask_exercise, exercise="C"), pattern='C'),
                    CallbackQueryHandler(partial(ask_exercise, exercise="R"), pattern='R'),
                ],
                "LOG_PU": [MessageHandler(Filters.all, callback=partial(log_exercise, exercise="PU"))],
                "LOG_C": [MessageHandler(Filters.all, callback=partial(log_exercise, exercise="C"))],
                "LOG_R": [MessageHandler(Filters.all, callback=partial(log_exercise, exercise="R"))],
                "choose_exercise": [CallbackQueryHandler(choose_exercise_query, pattern="track_exercise")]
            },
            fallbacks=[CommandHandler('start', start)],
            per_message=False
        )
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(CommandHandler("add_entry", log_exercise))
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("get_one", get_one))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
