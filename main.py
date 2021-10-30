import os
# Import necessary libraries:
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton  
 #upm package(python-telegram-bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from db import Database


db = Database()
db.create_tables()

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("Track Exercise", callback_data='1')],
        [InlineKeyboardButton("Retrieve", callback_data='2')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "from_start"


    

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("shape is: ")

'''
def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if query.data == "2":
      a = db.get_all()

    query.edit_message_text(text=a)
'''


def log(update: Update, context: CallbackContext) -> None:
  db.insert_entry(update.message.from_user.username, update.message.text, 3, 2)

def get_one(update: Update, context: CallbackContext) -> None:
  query = update.callback_query
  query.answer()
  query.edit_message_text(db.get_all())

def choose_exercise(update: Update, context: CallbackContext):
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

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            "from_start": [
                CallbackQueryHandler(choose_exercise, pattern='1'),
                CallbackQueryHandler(get_one, pattern='2')
            ],
            "selected_exercise": [
                MessageHandler(choose_exercise, pattern='1'),
                MessageHandler(get_one, pattern='2')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
      per_message=True
    )
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    conv_handler)
    dispatcher.add_handler(CommandHandler("add_entry", log))
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
