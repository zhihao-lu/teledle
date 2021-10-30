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
  update.message.reply_text(db.get_all())

def track_exercise(update: Update, context: CallbackContext):
  query = update.callback_query
  query.answer()

  keyboard = [
    [InlineKeyboardButton("Pull ups", callback_data='PU'),
    InlineKeyboardButton("Core", callback_data='C'),
    InlineKeyboardButton("Run", callback_data='R')]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(
    text="Choose exercise: ", reply_markup=reply_markup
  )

def main():

    updater = Updater(os.getenv("TOKEN"))
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
      entry_points=[CommandHandler('start', start)],
      states={
        "1": [CallbackQueryHandler(track_exercise)],
        "2": [CallbackQueryHandler(get_one)]
          },
      fallbacks=[CommandHandler('start', start)],
    )


    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add_entry", log))
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("get_one", get_one))
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, log))
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
