# TO DO
# multiple people can use at once
# admin mode

import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    ConversationHandler
from db import Database
from functools import partial, wraps

db = Database()
db.create_tables()

keyboard = [
    [InlineKeyboardButton("Track Exercise", callback_data='track_exercise')],
    [InlineKeyboardButton("Delete Exercise", callback_data='delete_exercise')],
    [InlineKeyboardButton("View History", callback_data='view_history')],
    [InlineKeyboardButton("Leaderboards", callback_data='leaderboard')]
]
main_keyboard = InlineKeyboardMarkup(keyboard)

LIST_OF_ADMINS = [148721731]


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def start(update: Update, context):

    update.message.reply_text('Please select one of the options:', reply_markup=main_keyboard)


def show_back_home(update, context):
    query = update.callback_query
    query.answer()

    text = "Welcome back home! Please select one of the options:"
    query.edit_message_text(text, reply_markup=main_keyboard)
    return ConversationHandler.END


def log_exercise(update, context, exercise=""):
    name = update.message.from_user.first_name
    tele = update.message.from_user.username
    score = update.message.text

    keyboard = [
        [InlineKeyboardButton("Record another", callback_data='track_exercise')],
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if exercise == "Run":
        try:
            score = float(score)
            if score < 0:
                raise ValueError
            db.insert_entry(name, tele, exercise, score)
            update.message.reply_text(f"Success! Recorded {score} km for {name}.", reply_markup=reply_markup)
        except ValueError:
            update.message.reply_text(f"Input is wrong, please try again or record 0 km to exit.")
            return "LOG_" + "R"

    else:
        try:
            score = int(score)
            if score < 0:
                raise ValueError
            db.insert_entry(name, tele, exercise, score)
            update.message.reply_text(f"Success! Recorded {score} reps for {name}.", reply_markup=reply_markup)
        except ValueError:
            update.message.reply_text(f"Input is wrong, please try again or record 0 reps to exit.")
            return "LOG_" + exercise[0]
    return ConversationHandler.END


def ask_exercise(update, context, exercise=""):
    query = update.callback_query
    query.answer()

    if exercise == "P":
        query.edit_message_text("Pull ups selected. Please enter how many pull ups you have done:")
        return "LOG_P"

    elif exercise == "C":
        query.edit_message_text("Core selected. Please enter how many you have done:")
        return "LOG_C"
    elif exercise == "R":
        query.edit_message_text("Run selected. Please enter how far you have ran in km (e.g. 4.6):")
        return "LOG_R"


def choose_exercise(update, context):
    keyboard = [
        [InlineKeyboardButton("Pull ups", callback_data='P'),
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
        [InlineKeyboardButton("Pull ups", callback_data='P'),
         InlineKeyboardButton("Core", callback_data='C'),
         InlineKeyboardButton("Run", callback_data='R')],
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Choose exercise: ", reply_markup=reply_markup
    )

    return "selected_exercise"


def delete_exercise(update, context):
    pass


def delete_exercise_query(update, context, offset=0, limit=5):
    query = update.callback_query
    query.answer()
    if "next_page" in query.data:
        offset = int(query.data[10:])

    history = db.get_user_history(query.from_user.username, offset)
    history = [list(map(lambda x: str(x), entry)) for entry in history]
    keyboard = [[InlineKeyboardButton(entry[3][5:10] + ": " + str(entry[2]) + " " + entry[1],
                                      callback_data=",".join(entry))] for entry in history]
    keyboard.append([InlineKeyboardButton("More entries", callback_data=f"next_page_{offset + limit}")])
    keyboard.append([InlineKeyboardButton("Back", callback_data="return_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Showing entries {offset} to {offset + limit}: ", reply_markup=reply_markup
    )

    return "selected_delete"


def confirm_delete(update, context):
    query = update.callback_query
    entry = query.data
    entry = entry.split(",")

    keyboard = [
        [InlineKeyboardButton("Confirm", callback_data=str(entry[0]))],
        [InlineKeyboardButton("Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Are you sure you want to delete {entry[3][5:10]}" + ': ' + str(entry[2]) + " " + entry[1] + '?'
        , reply_markup=reply_markup
    )

    return "confirm_delete"


def process_delete(update, context):
    query = update.callback_query
    query.answer()
    rowid = int(query.data)

    db.delete_entry(rowid)


    keyboard = [
        [InlineKeyboardButton("Delete another", callback_data='delete_exercise')],
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(f"Success! Deleted entry.", reply_markup=reply_markup)


def leaderboard(update, context):
    query = update.callback_query
    query.answer()

    w, all_time = db.get_leaderboards()

    all_time = "All time leaders \n" + all_time
    w = "This week's leaders \n" + w + "\n \n"

    keyboard = [
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(w + all_time, reply_markup=reply_markup)

    return ConversationHandler.END


def view_history(update, context):
    query = update.callback_query
    tele = query.from_user.username
    query.answer()

    s = db.get_history()

    keyboard = [
        [InlineKeyboardButton("Back", callback_data='return_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(s, reply_markup=reply_markup)

    return ConversationHandler.END


# Admin functions
@restricted
def get_one(update, context):
    update.message.reply_text(db.get_all())


@restricted
def drop(update, context):
    db.drop_table("")


def main():
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ['TOKEN'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(show_back_home, pattern="return_menu"))
    dispatcher.add_handler(CallbackQueryHandler(leaderboard, pattern="leaderboard"))
    dispatcher.add_handler(CallbackQueryHandler(view_history, pattern="view_history"))
    dispatcher.add_handler(CommandHandler("add_entry", log_exercise))

    # Add exercise entry
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("track_exercise", choose_exercise),
                          CallbackQueryHandler(choose_exercise_query, pattern="track_exercise")],
            states={
                "selected_exercise": [
                    CallbackQueryHandler(partial(ask_exercise, exercise="P"), pattern='P'),
                    CallbackQueryHandler(partial(ask_exercise, exercise="C"), pattern='C'),
                    CallbackQueryHandler(partial(ask_exercise, exercise="R"), pattern='R')
                ],
                "LOG_P": [MessageHandler(Filters.all, callback=partial(log_exercise, exercise="Pull Ups"))],
                "LOG_C": [MessageHandler(Filters.all, callback=partial(log_exercise, exercise="Core"))],
                "LOG_R": [MessageHandler(Filters.all, callback=partial(log_exercise, exercise="Run"))],
                "choose_exercise": [CallbackQueryHandler(choose_exercise_query, pattern="track_exercise")],
                # "TIMEOUT": [CallbackQueryHandler(choose_exercise_query, pattern="track_exercise")]
            },
            fallbacks=[CallbackQueryHandler(choose_exercise_query, pattern="track_exercise")],
            per_message=False
        )
    )

    # Delete entry
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("delete_exercise", delete_exercise),
                          CallbackQueryHandler(delete_exercise_query, pattern="delete_exercise")],
            states={
                "selected_delete": [
                    CallbackQueryHandler(confirm_delete, pattern=("^\d")),
                    CallbackQueryHandler(delete_exercise_query, pattern="^next_page")

                ],
                "confirm_delete": [CallbackQueryHandler(process_delete, pattern="\d+"),
                                   CallbackQueryHandler(delete_exercise_query, pattern="back")],
            },
            fallbacks=[CallbackQueryHandler(delete_exercise_query, pattern="delete_exercise")],
            per_message=False
        )
    )

    # Admin commands
    dispatcher.add_handler(CommandHandler("get_one", get_one))
    dispatcher.add_handler(CommandHandler("drop", drop))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
